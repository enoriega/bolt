#!/usr/bin/env python
# coding: utf-8

from __future__ import division

import re
import numpy as np
from sklearn.datasets.base import Bunch
from sklearn.metrics import classification_report, confusion_matrix, Scorer
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
import pickle



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
        if aligned_hyp[i] == '*DELETE*':
            count += 1
        else:
            break
    for i in xrange(idx+1, len(aligned_hyp)):
        if aligned_hyp[i] == '*DELETE*':
            count += 1
        else:
            break
    return count



def feature_vectors(hyp, aligned_hyp, sausage, score, ascore, lscore):
    entropies = [entropy(slot) for slot in sausage.sausage]
    len_ratio = len(hyp) / len(aligned_hyp)
    num_deletes = sum(1 for tok in aligned_hyp if tok == '*DELETE*')
    vec = [sausage.score_hyp(aligned_hyp), score, ascore, lscore,
           min(entropies), max(entropies), num_deletes, len_ratio]
    return vec



def get_dataset():
    target_names = np.char.array(['OK', 'ERROR'])
    target = []
    data = []
    for name, ref, hyp, sausage, lattice, nbest in zip(*read_output()):
        # print name
        tag = int(ref != hyp)
        ref = get_tokens(ref)
        hyp = get_tokens(hyp)
        sausage = Sausage.from_file(sausage)
        try:
            aligned_hyp, score = sausage.align_hyp(' '.join(hyp))
        except:
            continue    
        target.append(tag)
        ascore, lscore, _ = read_nbest(nbest)[0]
        v = feature_vectors(hyp, aligned_hyp, sausage, score, ascore, lscore)
        data.append(v)
    data = scale(np.array(data))
    # data = np.array(data)
    target = np.array(target)
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

@Scorer
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
    print
    print 'n_samples =', data.data.shape[0]
    print 'n_features =', data.data.shape[1]
    
    print 'splitting data ...'
    # fselect = SelectKBest(f_classif)
    # fselect.fit(data.data, data.target)
    # data.data = fselect.transform(data.data)
    # split into train and test datasets
    X_train, X_test, y_train, y_test = train_test_split(data.data, data.target, test_size=0.25)

    print
    params = {'penalty': ['l1','l2'], 'C': [0.01, 0.1, 1, 10, 100, 1000]}
    clf = GridSearchCV(LogisticRegression(), params)
    test_classifier(clf, X_train, X_test, y_train, y_test)

    # Save the best estimator
    with open('logistic_regression.pickle', 'wb') as f:
        pickle.dump(clf.best_estimator_, f)

    clf = clf.best_estimator_
    y_predict = clf.predict(data.data)
    print confusion_matrix(data.target, y_predict) 
