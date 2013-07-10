#!/usr/bin/env python

from __future__ import division

import re
import matplotlib.pyplot as plt
from boltdata import read_output
from sausages import read_nbest



def get_tokens(s):
    func = lambda x: not re.match(r'^\*+$', x)
    return filter(func, s.lower().split())

def get_prob(n):
    count = 0
    total = 0
    for name, ref, hyp, sau_f, latt_f, nbest_f in zip(*read_output()):
        ref = ' '.join(get_tokens(ref))
        total += 1
        nbest = [' '.join(x[2]) for x in read_nbest(nbest_f)]
        if ref in nbest[:n]:
            count += 1
    return count / total


if __name__ == '__main__':
    ns = range(1, 21)
    probs = []
    for n in ns:
        print n
        probs.append(get_prob(n))

    plt.plot(ns, probs)
    plt.xlabel('n')
    plt.ylabel('Pr(ref in nbest)')
    plt.ylim([0,1])
    plt.show()
