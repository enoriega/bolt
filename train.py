#!/usr/bin/env python
# coding: utf-8

from __future__ import division

import re
import numpy as np
from sklearn.datasets.base import Bunch
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.cross_validation import train_test_split
from sklearn.naive_bayes import MultinomialNB
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC, LinearSVC
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from nltk.probability import entropy
from boltdata import read_output
from sausages import Sausage
from sausage_aligner import ConvergenceError



def get_tokens(s):
    func = lambda x: not re.match(r'^\*+$', x)
    return filter(func, s.lower().split())



def get_labels(refs, hyps, sausages, lattices):
    labels = []
    for ref, hyp, sausage, l in zip(refs, hyps, sausages, lattices):
        print ref
        print hyp
        # ref = get_tokens(ref)
        hyp, score = sausage.align_hyp(hyp)
        print hyp
        labels = sausage.tag_ref(ref, hyp)
        print labels
        print
    return np.char.array(labels)



def feature_vectors(sausage):
    for i in xrange(sausage.num_slots()):
        prev_slot = sausage.sausage[i-1] if i > 0 else None
        curr_slot = sausage.sausage[i]
        next_slot = sausage.sausage[i+1] if i < sausage.num_slots()-1 else None

        vec = np.zeros(20)

        best = curr_slot.max()
        probs = [curr_slot.prob(s) for s in curr_slot.samples()]
        vec[0] = sausage.num_slots()
        vec[1] = i
        vec[2] = np.mean(probs)
        vec[3] = np.std(probs)
        vec[4] = entropy(curr_slot)
        vec[5] = curr_slot.prob(best)
        vec[6] = 0 if best == '*DELETE*' else len(best)
        vec[7] = int(best == '*DELETE*')

        if prev_slot:
            best = prev_slot.max()
            probs = [prev_slot.prob(s) for s in prev_slot.samples()]
            vec[8] = np.mean(probs)
            vec[9] = np.std(probs)
            vec[10] = entropy(prev_slot)
            vec[11] = prev_slot.prob(best)
            vec[12] = 0 if best == '*DELETE*' else len(best)
            vec[13] = int(best == '*DELETE*')

        if next_slot:
            best = next_slot.max()
            probs = [next_slot.prob(s) for s in next_slot.samples()]
            vec[14] = np.mean(probs)
            vec[15] = np.std(probs)
            vec[16] = entropy(next_slot)
            vec[17] = next_slot.prob(best)
            vec[18] = 0 if best == '*DELETE*' else len(best)
            vec[19] = int(best == '*DELETE*')

        yield vec



def get_dataset():
    target_names = np.char.array(['OK', 'ERROR'])
    target = []
    data = []
    for name, ref, hyp, sausage, lattice, nbest in zip(*read_output()):
        print name
        sausage = Sausage.from_file(sausage)
        try:
            hyp, score = sausage.align_hyp(hyp)
            labels = np.char.array(sausage.tag_ref(ref, hyp))
        except Exception:
            print 'skipping', name, '...'
            continue
        print ref
        print hyp
        print labels
        print '-' * 70
        # create targets based on target_names
        tgt = np.empty(labels.shape)
        tgt[labels=='OK'] = 0
        tgt[labels!='OK'] = 1
        target.append(tgt)
        for v in feature_vectors(sausage):
            data.append(v)
    data = np.array(data)
    target = np.concatenate(target)
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



if __name__ == '__main__':
    print 'reading data ...'
    data = get_dataset()
    print 'n_samples =', data.data.shape[0]
    print 'n_features =', data.data.shape[1]
    
    print 'splitting data ...'
    # split into train and test datasets
    X_train, X_test, y_train, y_test = train_test_split(data.data, data.target, test_size=0.25)

    print
    test_classifier(LogisticRegression(), X_train, X_test, y_train, y_test)
    test_classifier(MultinomialNB(), X_train, X_test, y_train, y_test)
    test_classifier(DecisionTreeClassifier(), X_train, X_test, y_train, y_test)
    test_classifier(RandomForestClassifier(), X_train, X_test, y_train, y_test)
    test_classifier(GradientBoostingClassifier(), X_train, X_test, y_train, y_test)
    # test_classifier(LinearSVC(), X_train, X_test, y_train, y_test)
    # test_classifier(SVC(), X_train, X_test, y_train, y_test)
