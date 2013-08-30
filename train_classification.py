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
from sausages import Sausage, read_nbest, read_word_scores

from bolt_learning import CLASSIFICATOR_FILE_NAME
from bolt_learning.features import get_classification_dataset
import pickle


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
    data = get_classification_dataset()
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
    with open(CLASSIFICATOR_FILE_NAME, 'wb') as f:
        pickle.dump(clf.best_estimator_, f)

    clf = clf.best_estimator_
    y_predict = clf.predict(data.data)
    print confusion_matrix(data.target, y_predict) 
