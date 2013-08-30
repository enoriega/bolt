#!/usr/bin/env python

from __future__ import division

import operator
import itertools
from bolt_learning import sausage_aligner
import gzip
from math import log
from nltk.probability import DictionaryProbDist
from bolt_learning import DELETE_TOKEN
from bolt_learning.utils import get_tokens


def read_word_scores(filename):
    scores = {}
    with open(filename) as f:
        for line in f:
            if line.startswith('info'):
                toks = line.split()[2:]
                word = toks[0]
                start = float(toks[1])
                duration = float(toks[2])
                ascore = float(toks[3])
                lscore = float(toks[4])
                scores[word] = (start, duration, ascore, lscore)
    return scores


def read_sausage(filename, normalize=True):
    """gets a filename and returns a list of probability distributions"""
    sausage = []
    with open(filename) as f:
        for line in f:
            if line.startswith('align'):
                # align a w1 p1 w2 p2 ...
                # split line and ignore first two tokens
                tokens = line.lower().split()[2:]
                words = tokens[::2]
                probs = tokens[1::2]
                prob_dict = {w:float(p) for w,p in zip(words, probs)}
                slot = DictionaryProbDist(prob_dict, normalize=normalize)
                sausage.append(slot)
    # first and last slots must be sentence boundaries
    assert sausage[0].samples() == ['<s>']
    assert sausage[-1].samples() == ['</s>']
    # return sausage without sentence boundaries
    return sausage[1:-1]
    
def read_nbest(nbest_file):
    """reads and parses the nbest gzip file"""
    nbest = []
    with gzip.open(nbest_file) as f:
        for line in f:
            tokens = line.split()
            asr_score = float(tokens[0])
            lm_score = float(tokens[1])
            # Remove pause tokens and <s>, </s> tokens
            hyp = [token for token in tokens[4:-1] if token != '-pau-']
            
            nbest.append((asr_score, lm_score, hyp))
    return nbest
    



class Sausage(object):
    SPECIAL_TOKENS = ('<s>', '</s>', DELETE_TOKEN)

    def __init__(self, sausage, nbests = None, id = None):
        self.sausage = sausage
        
        self.nbests = nbests
        self.id = id

    @classmethod
    def from_file(cls, filename, nbest_file = None, id = None, normalize=True):
        sausage = read_sausage(filename, normalize=normalize)
        #sausage_alt = sausage_aligner.parse_sausage(filename)
        
        if nbest_file != None:
            nbest = read_nbest(nbest_file)
        else:
            nbest = None
            
        return cls(sausage, nbest, id)
        

    def num_slots(self):
        return len(self.sausage)

    def best_hyp(self):
        """returns the best hyp for the sausage"""
        return [slot.max() for slot in self.sausage]

    def all_hyps(self):
        """generate all possible hyps unordered"""
        return itertools.product(*[slot.samples() for slot in self.sausage])

    def all_scored_hyps(self):
        """returns (score, hyp) tuples"""
        for hyp in self.all_hyps():
            yield (self.score_hyp(hyp), hyp)

    def score_hyp(self, hyp):
        """gets a hyp and returns its score"""
        # multiply posterior probability for each token in hyp
        probs = [slot.prob(w) for slot,w in zip(self.sausage, hyp)]
        return reduce(operator.mul, probs)
        
    def logscore_hyp(self, hyp):
        """gets a hyp and returns its score"""
        # multiply posterior probability for each token in hyp
        probs = [slot.logprob(w) for slot,w in zip(self.sausage, hyp)]
        return reduce(operator.add, probs)

    #XXX Probably this is now redundant after reading the nbest file
    def nbest(self, n=None):
        """returns n-best hyps sorted by score in descending order"""
        # NOTE this may be expensive
        scored_hyps = sorted(self.all_scored_hyps(), reverse=True)
        return scored_hyps[:n] if n is not None else scored_hyps

    def clean_hyp(self, hyp):
        """remove special tokens"""
        return filter(lambda t: t not in self.SPECIAL_TOKENS, hyp)
        
    def align_hyp(self, hyp):
        """Aligns a hyp to this sausage"""
        
        if type(hyp) == str:
            hyp = get_tokens(hyp)
            # Parse the hyp into tokens
            # hyp = hyp.split(' ')
            # hyp = [t.lower() for t in hyp if t != ''] # Get rid of the nasty empty tokens and lowercase all
            # hyp = [t for t in hyp if t.strip('*') != ''] # Get rid of the nasty ** tokens
        
        # Perform alignment
        align, score = sausage_aligner.align_hyp(self.sausage, hyp)
        
        # Validate correctness
        assert(sausage_aligner.validate_alignment(self.sausage, align, hyp) == True)

        # align = ['*DELETE*' if w == DELETE_TOKEN else w for w in align]
        
        return align, score
        
    def aligned_nbests(self):
        """Returns the aligned version of the nbests read from file"""
        ret = []
        index = 1
        for nbest in self.__nbests:
            try:
                # Align the hyp
                aligned_hyp, score = self.align_hyp(nbest[2])
            
                vals = { 'ASR_SCORE':nbest[0], 'LM_SCORE':nbest[1],
                        'SAUSAGE_SCORE':self.logscore_hyp(nbest[2]),
                        'ALIGN_SCORE':score, 'HYP':aligned_hyp }
                
                # This ensures that the resulting alignment is only reported if
                # is a valid alignment, (meaning that the hyp came form the sausage)
                
                ret.append(vals)
                    
            except:
                # This shouldn't happen once the bug is fixed
                print "Something went wrong with the alignment, please report this to Enrique: %s - s%s" % (self.id, index)
            finally:
                index += 1
                
        return ret
        
    @classmethod    
    def tag_ref(cls, ref, align_hyp):
        """Tags an aligned hyp given a ref"""
        
        ref = get_tokens(ref)
        # ref = ref.split(' ')
        # ref = [t.lower() for t in ref if t != ''] # Get rid of the nasty empty tokens and lowercase all
        # ref = [t for t in ref if t.strip('*') != ''] # Get rid of the nasty ** tokens
        
        # TEST
        # If ref is larger than align_hyp, pad it with delete tokens for the alineation and scoring
        #print align_hyp
        #for i in range(max(0, len(ref) - len(align_hyp))):
        #        align_hyp.append(DELETE_TOKEN)
 
        #print align_hyp
        
        # Align the ref to the already aligned hyp
        if len(ref) > len(align_hyp):
            align_ref = sausage_aligner.align_ref_long(align_hyp, ref)
        else:
            align_ref = sausage_aligner.align_ref(align_hyp, ref)
        
        
        # align_ref = ['*DELETE*' if w == DELETE_TOKEN else w for w in align_ref]
        # Generate tags
        return align_ref, sausage_aligner.score(align_ref, align_hyp)
        
