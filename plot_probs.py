#!/usr/bin/env python

from __future__ import division

from linear_regression import fixable, unfixable
import re
import matplotlib.pyplot as plt
from boltdata import read_output
from sausages import read_nbest
import sys


def get_tokens(s):
    func = lambda x: not re.match(r'^\*+$', x)
    return filter(func, s.lower().split())

def get_prob(n, names=None):
    count = 0
    total = 0
    for name, ref, hyp, sau_f, latt_f, nbest_f in zip(*read_output()):
        if names is not None and name not in names:
            continue
            ref = ' '.join(get_tokens(ref))
            total += 1
            nbest = [' '.join(x[2]) for x in read_nbest(nbest_f)]
            if ref in nbest[:n]:
                count += 1
    return count / total

def get_counts(n, names=None):
    count = 0
    total = 0
    for name, ref, hyp, sau_f, latt_f, nbest_f in zip(*read_output()):
        if names is not None and name not in names:
            continue
            ref = ' '.join(get_tokens(ref))
            total += 1
            nbest = [' '.join(x[2]) for x in read_nbest(nbest_f)]
            if ref in nbest[:n]:
                count += 1
    return count


def myplot(ns, probs):
    plt.plot(ns, probs)
    plt.xlabel('n')
    plt.ylabel('Pr(ref in nbest)')
    #plt.ylim([0,1])
    plt.show()

if __name__ == '__main__':
    ns = range(1, 21)
    probs = []

    if len(sys.argv) == 2:
        names = fixable if sys.argv[1] == "fixable" else unfixable
    else:
        names = None

    for n in ns:
        print n
        probs.append(get_prob(n, names))

    myplot(ns, probs)
