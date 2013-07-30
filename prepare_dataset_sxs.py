#!/usr/bin/env python
# coding: utf-8

from __future__ import division

import re
import pickle
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
from difflib import SequenceMatcher

delete_token = '*delete*'

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
        if aligned_hyp[i] == delete_token:
            count += 1
        else:
            break
    for i in xrange(idx+1, len(aligned_hyp)):
        if aligned_hyp[i] == delete_token:
            count += 1
        else:
            break
    return count



def feature_vectors(hyp, aligned_hyp, sausage, score, ascore, lscore):
    '''returns a feature vector for the logistic regression'''
    entropies = [entropy(slot) for slot in sausage.sausage]
    len_ratio = len(hyp) / len(aligned_hyp)
    num_deletes = sum(1 for tok in aligned_hyp if tok == delete_token)
    vec = [sausage.score_hyp(aligned_hyp), score, ascore, lscore,
           min(entropies), max(entropies), num_deletes, len_ratio]
    return vec

def get_dataset():
    '''returns a data set taylored for the logistic regression'''
    target_names = np.char.array(['OK', 'ERROR'])
    target = []
    data = []
    names = []
    hyps = []
    for name, ref, hyp, sausage, lattice, nbest in zip(*read_output()):
        # print name
	names.append(name)
	hyps.append(hyp)
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
    np_names = np.char.array(names)
    hyps = np.char.array(hyps)
    return Bunch(data=data, target=target, target_names=target_names, names = np_names, hyps = hyps)

def get_dataset_linear_regression(ids=None):
    '''returns a dataset taylored for the linear regression'''
    
    target = []
    data = []
    names = []
    hyps = []

    if ids is not None:
        with open(ids, 'r') as f:
            ids = pickle.load(f)

 
    skipped = 0
    for name, ref, hyp, sausage, lattice, nbest in zip(*read_output()):

	if ids is not None and name not in ids:
            skipped += 1
            continue

        names.append(name)
	hyps.append(hyp)
        ref = get_tokens(ref)
	#dirty_hyp = hyp.lower().split()
  	hyp = get_tokens(hyp)
        sausage = Sausage.from_file(sausage)
        try:
            aligned_hyp, score = sausage.align_hyp(' '.join(hyp))
        except:
            continue    
	#Add the WER to targets
	target.append(WER(ref, hyp))
        ascore, lscore, _ = read_nbest(nbest)[0]
        v = [lscore, score, len([t for t in aligned_hyp if t == delete_token]), len(hyp), 1.0/float(len(hyp))]
        data.append(v)
    data = scale(np.array(data))
    # data = np.array(data)
    target = np.array(target)
    np_names = np.char.array(names)
    hyps = np.char.array(hyps)
    return Bunch(data=data, target=target, names = np_names, hyps = hyps)

def align(x,y):
    s = SequenceMatcher()
    s.set_seq1(x)
    s.set_seq2(y)
    return s.get_opcodes()

def WER (ref, hyp) :
    # Computes Word Error Rate via sequence alignment
    opcodes = align(ref,hyp)
    errors = 0
    for code in opcodes:
        if code[0] ==   'replace': errors += 2 * (code[4] - code[3])
        elif code[0] == 'insert': errors += (code[4] - code[3])
        elif code[0] == 'delete': errors += (code[2] - code[1])
    #if len(ref) > 0 and len(hyp) > 0: return (2 * errors) / float(len(ref)+len(hyp))
    if len(ref) > 0 and len(hyp) > 0: return errors
    else: return 0
