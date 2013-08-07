#!/usr/bin/env python
# coding: utf-8

from __future__ import division

import re
import numpy as np
from sklearn.datasets.base import Bunch
from sklearn.metrics import classification_report, confusion_matrix, make_scorer
from sklearn.cross_validation import train_test_split
from sklearn.naive_bayes import GaussianNB
from sklearn.linear_model import LogisticRegression, PassiveAggressiveClassifier
from sklearn.svm import SVC, LinearSVC
from sklearn.tree import DecisionTreeClassifier, ExtraTreeClassifier
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier, ExtraTreesClassifier
from sklearn.grid_search import GridSearchCV
from sklearn.preprocessing import scale
from sklearn.feature_selection import f_classif, SelectKBest
from nltk.probability import entropy
from boltdata import read_output
from sausages import Sausage, read_nbest, read_word_scores



def get_tokens(s):
    func = lambda x: not re.match(r'^\*+$', x)
    return filter(func, s.lower().split())



def get_stats(slot):
    probs = [slot.prob(s) for s in slot.samples()]
    mean = np.mean(probs)
    stdev = np.std(probs)
    ent = entropy(slot)
    return mean, stdev, ent

def count_deletes(aligned_hyp, idx):
    count = 0
    for i in reversed(xrange(idx)):
        if aligned_hyp[i] == '*delete*':
            count += 1
        else:
            break
    for i in xrange(idx+1, len(aligned_hyp)):
        if aligned_hyp[i] == '*delete*':
            count += 1
        else:
            break
    return count



def feature_vectors(aligned_hyp, sausage, score, ascore, lscore, word_scores):
    prev_tok = None
    for i,token in enumerate(aligned_hyp):

        curr_mean, curr_stdev, curr_ent = get_stats(sausage.sausage[i])
        prev_mean = prev_stdev = prev_ent = 0
        if i > 0:
            prev_mean,prev_stdev,prev_ent = get_stats(sausage.sausage[i-1])
        next_mean = next_stdev = next_ent = 0
        if i < sausage.num_slots() - 1:
            next_mean,next_stdev,next_ent = get_stats(sausage.sausage[i])

        wscores = word_scores[token]
        prev_wscores = word_scores[prev_tok] if prev_tok else None
        vec = [score, ascore, lscore,
               sausage.score_hyp(aligned_hyp),
               sausage.num_slots(),
               sausage.sausage[i].prob(token),
               wscores[0], wscores[1], wscores[2], wscores[3],
               prev_mean, prev_stdev, prev_ent,
               curr_mean, curr_stdev, curr_ent,
               next_mean, next_stdev, next_ent,
               count_deletes(aligned_hyp, i),
               # int((prev_wscores[0] < wscores[0]) if prev_wscores else 1),
               int(sausage.sausage[i].max() == token),
               int(sausage.sausage[i].max() == '*delete*'),
               int('*delete*' in sausage.sausage[i].samples())]

        prev_tok = token
        yield vec



def get_dataset():
    target_names = np.char.array(['OK', 'ERROR'])
    target = []
    data = []
    error_count = 0
    i = 0
    for name, ref, hyp, sausage, lattice, nbest in zip(*read_output()):
        i += 1
        ref = get_tokens(ref)
        hyp = get_tokens(hyp)
        errors = set(ref).symmetric_difference(set(hyp))
        # tags = [int(w in errors) for w in hyp]
        word_scores = read_word_scores(sausage)
        word_scores['*delete*'] = (0,0,0,0)
        sausage = Sausage.from_file(sausage)
        try:
            aligned_hyp, score = sausage.align_hyp(' '.join(hyp))
            aligned_ref, tags = sausage.tag_ref(' '.join(ref), aligned_hyp)
        except:
            error_count += 1
            continue
        print '-' * 50
        print aligned_ref
        print aligned_hyp
        print tags
        # everything that is not ok is an error
        tags = [int(s!='OK') for s in tags]
        target.append(tags)
        ascore, lscore, _ = read_nbest(nbest)[0]
        for v in feature_vectors(aligned_hyp, sausage, score, ascore, lscore, word_scores):
            print v
            data.append(v)
    data = scale(np.array(data))
    # data = np.array(data)
    target = np.concatenate(target)
    print 'ERRORS ',error_count, i
    return Bunch(data=data, target=target, target_names=target_names)



def test_classifier(clf, X_train, X_test, y_train, y_test):
    print clf
    clf = clf.fit(X_train, y_train)
    y_pred = clf.predict(X_test)
    print
    print classification_report(y_test, y_pred, target_names=data.target_names)
    print 'confusion matrix'
    print confusion_matrix(y_test, y_pred)
    print


@make_scorer
def my_score(ground_truth, predictions):
    cls = 1
    tp = fp = tn = fn = 0
    for t,p in zip(ground_truth, predictions):
        if p == cls:
            if t == p:
                tp += 1
            else:
                fp += 1
        else:
            if t == p:
                tn += 1
            else:
                fn += 1
    return 0 if tp + fp == 0 else tp / (tp + fp)



if __name__ == '__main__':
    print 'reading data ...'
    data = get_dataset()
    print 'n_samples =', data.data.shape[0]
    print 'n_features =', data.data.shape[1]
    
    print 'splitting data ...'
    # fselect = SelectKBest(f_classif)
    # fselect.fit(data.data, data.target)
    # data.data = fselect.transform(data.data)
    # split into train and test datasets
    X_train, X_test, y_train, y_test = train_test_split(data.data, data.target, test_size=0.25)

    print
    params = {'penalty': ['l1','l2'], 'C': [0.01, 0.1, 1, 10, 100]}
    clf = GridSearchCV(LogisticRegression(), params, scoring=my_score)
    test_classifier(clf, X_train, X_test, y_train, y_test)

    params = {'loss': ['hinge', 'squared_hinge'], 'C': [0.01, 0.1, 1, 10, 100]}
    clf = GridSearchCV(PassiveAggressiveClassifier(), params, scoring=my_score)
    test_classifier(clf, X_train, X_test, y_train, y_test)

    test_classifier(GaussianNB(), X_train, X_test, y_train, y_test)

    params = {'criterion': ['gini', 'entropy'],
              'max_features': ['sqrt', 'log2', 'auto', None]}
    clf = GridSearchCV(DecisionTreeClassifier(), params, scoring=my_score)
    test_classifier(clf, X_train, X_test, y_train, y_test)

    clf = GridSearchCV(ExtraTreeClassifier(), params, scoring=my_score)
    test_classifier(clf, X_train, X_test, y_train, y_test)

    params['n_estimators'] = [2,5,10,15]
    clf = GridSearchCV(RandomForestClassifier(), params, scoring=my_score)
    test_classifier(clf, X_train, X_test, y_train, y_test)

    clf = GridSearchCV(ExtraTreesClassifier(), params, scoring=my_score)
    test_classifier(clf, X_train, X_test, y_train, y_test)

    test_classifier(GradientBoostingClassifier(), X_train, X_test, y_train, y_test)

    params = {'loss': ['l1','l2'], 'C': [0.01, 0.1, 1, 10, 100]}
    clf = GridSearchCV(LinearSVC(), params, scoring=my_score)
    test_classifier(clf, X_train, X_test, y_train, y_test)

    params = {'kernel': ['rbf','poly','sigmoid','linear'], 'C': [0.01, 0.1, 1, 10, 100]}
    clf = GridSearchCV(SVC(), params, scoring=my_score)
    test_classifier(clf, X_train, X_test, y_train, y_test)
