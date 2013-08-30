# coding: utf-8

from __future__ import division

import os, re, gzip
from glob import glob
import numpy as np



DATADIR = os.path.expanduser('/bolten/arizona_recognizer_test')
# DATADIR = os.path.expanduser('~/Downloads/arizona_recognizer_test')
OUTPUTDIR = os.path.join(DATADIR, 'output')
VOCABFILE = os.path.join(DATADIR, 'models',
                         'package_16K-EN_20120703_wfst+1gr-v2',
                         'Grammars', 'lm', 'step060.rec_lm.1bo.fixed.gz')



def read_vocabulary(filename=VOCABFILE):
    """gets a unigram language model and returns the vocabulary"""
    vocabulary = set()
    with gzip.open(filename) as f:
        for line in f:
            match = re.search(r'^.+\t(.+)$', line)
            if match:
                vocabulary.add(match.group(1))
    return vocabulary



def read_log(filename):
    names = []
    refs = []
    hyps = []
    with open(filename) as f:
        for line in f:
            line = line.strip()
            if line.startswith('FILENAME:'):
                fname = os.path.basename(line[10:])
                name = os.path.splitext(fname)[0]
                names.append(name)
            elif line.startswith('REF:'):
                refs.append(line[5:])
            elif line.startswith('HYP:'):
                hyps.append(line[5:])
    return names, refs, hyps



def read_output(path=OUTPUTDIR):
    """read bolt data and return for each instance:
        - name
        - ref
        - hyp
        - sausage filename
        - lattice filename
        - nbest filename
    """
    all_names = []
    all_refs = []
    all_hyps = []
    all_sausages = []
    all_lattices = []
    all_nbests = []
    pattern = os.path.join(path, '*', 'log.txt')
    
    for logfile in glob(pattern):
        dirname = os.path.dirname(logfile)
        names, refs, hyps = read_log(logfile)
        all_names += names
        all_refs += refs
        all_hyps += hyps
        sausage = os.path.join(dirname, 'aligned_sausages', '%s.sausage')
        lattice = os.path.join(dirname, 'lattices', '%s.lattice')
        nbest = os.path.join(dirname, 'nbests', 's%s.nbest.gz')
        all_sausages += [sausage % n for n in names]
        all_lattices += [lattice % n for n in names]
        all_nbests += [nbest % i for i in xrange(1, len(names) + 1)]
    return all_names, all_refs, all_hyps, all_sausages, all_lattices, all_nbests



if __name__ == '__main__':
    names, refs, hyps, sausages, lattices, nbests = read_output()
    for name, ref, hyp in zip(names, refs, hyps):
        print 'NAME:', name
        print 'REF:', ref
        print 'HYP:', hyp
        print '-' * 70
