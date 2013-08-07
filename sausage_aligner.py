#!/usr/bin/python
from __future__ import print_function
import sys, os, pickle, re
import boltdata
from alignment.sequence import Sequence
from alignment.vocabulary import Vocabulary
from alignment.sequencealigner import SimpleScoring, StrictGlobalSequenceAligner

column_width = 15 # column width, must be larger than the length of the largest token in a slot
delete_token = '*delete*'
neg_inf = float('-inf')

vocabulary = boltdata.read_vocabulary()
    
    
def print_sausage(sausage):
    ''' Prints a sausage in a human-friendly fashion '''

    depth = max([len(slot.samples()) for slot in sausage])
    
    for i in range(depth):
        for j in range(len(sausage)):
            slot = [t.lower() for t in sausage[j].samples()]
            if i < len(slot):
                print( '%s' % slot[i], end='')
                for x in range(max(0, column_width - len(slot[i]))):
                    print(' ', end='')
            else:
                for x in range(column_width):
                    print(' ', end='')
        print() # New line
        
def print_align(align):
    ''' Prints an alignment in a human-friendly fashion '''
    
    for token in align:
        print(token, end='')
        for i in range(max(0, column_width - len(token))):
            print(' ', end='')
            
    print() # New line
    
    
def validate_hyp(sausage, hyp):
    ''' Validates that all the tokens in the hyp
        are also in the sausage '''
    
    # Special cases
    if len(hyp) == 0:
        return (False, None)
    ####
        
    vocab = set(arc for slot in sausage for arc in slot.samples())
    
    rouge_token = None
    
    valid = True
    
    for token in hyp:
            
        valid &= token in vocab
        if not valid:
            rouge_token = token
            break
        
    return valid, rouge_token
        

def align_hyp(sausage, hyp):
    ''' Aligns a hyp with a sausage
        hyp must be an iterable of strings and sausage must be a sausage list'''
        
        
    # Validate that the hyp is valid
    result = validate_hyp(sausage, hyp)
    if not result[0]:
        raise InvalidHypError(sausage, hyp, result[1])
        
    # Generate a zero-filled matrix
    
    m = len(hyp) + 1
    n = len(sausage) + 1
    
    M = [[0.0 for j in range(n)] for i in range(m)]
    
    # Add the -inf boundary conditions
    for i in range(1, m):
        M[i][0] = neg_inf
    
    # Do the dynamic programming
    for i in range(1, m):
        for j in range(1, n):
            
            tokens =  [a.lower() for a in sausage[j-1].samples()]
            prev_tokens = [a.lower() for a in sausage[j-2].samples()] if j > 1 else []
            scores = {a:sausage[j-1].prob(a) for a in sausage[j-1].samples()}

    
            token = hyp[i-1]
    
            # Case token not in slot
            if not token in tokens and not delete_token in tokens:
                M[i][j] = neg_inf
            # Case token not in slot but delete present
            elif not token in tokens and delete_token in tokens:
                M[i][j] = M[i][j-1]
            # Case token in slot and no other option
            elif token in tokens and (not delete_token in tokens or (j == 1 or not token in prev_tokens)):
                M[i][j] = max(M[i-1][j-1] + scores[token], M[i][j-1])
            # Case token could be either here or in the previous slot
            elif token in tokens and j >= 2 and delete_token in tokens and token in prev_tokens:
                M[i][j] = max(M[i-1][j-1] + scores[token], M[i][j-1])
            # Should never fall into here
            else:
                print(token, tokens, prev_tokens, "j:", j)
                raise Exception("Fell into the forbidden clause of the dynamic programming")
#     print_sausage(sausage)
#     print()
#     print(hyp)
#     print()
#     for i in range(m):
#         print(M[i])
#     print()
     
        
    # Just to verify that the method converged
    contains = False
    for i in range(m):
        if not M[i][-1] in (neg_inf, 0.0):
            contains = True
            break
            
    if not contains: raise ConvergenceError(M)
    ##########################################
    
    # Calculate the starting point for the recovery
    vector = [M[i][-1] for i in range(m)]
    x = vector.index(max(vector))
    y = n-1
                
    max_score = M[x][y]
    
    align = recovery_hyp(M, hyp, (x, y))
    
    return align, max_score
    
def recovery_hyp(M, hyp, point):
    ''' Recovers the alignment sequence from a dynamic programming '''
    m = len(M)
    n = len(M[0])
    
    i = point[0]
    j = point[1]
    
   # print('i:', i, 'j:', j)
    # Base case
    if i == 0:
        return [delete_token for l in range(j)]
    elif M[i][j] == M[i][j-1]:
        partial = recovery_hyp(M, hyp, (i, j-1))
        partial.append(delete_token)
        return partial
    elif M[i][j] > M[i][j-1]:
        partial = recovery_hyp(M, hyp[:-1], (i-1, j-1))
        partial.append(hyp[i-1])
        return partial
    else:
        raise Exception("Recovery: shouldn't be here")
        pass
        
        
def validate_alignment(sausage, align, hyp):
    ''' Returns true iff each element of the alignment is present on its correspondent
        sausage slot'''
    
    expected_deletes = len(align) - len(hyp)
    
    deletes = 0
    for i in range(len(align)):
        slot = [s.lower() for s in sausage[i].samples()]
        if not align[i] in slot:
            return False
            
        if align[i] == delete_token:
            deletes += 1
            
    if expected_deletes != deletes:
        return False
            
    return True
    
    
def align_ref(hyp, ref):
    ''' Aligns a ref to a sausage-aligned hype 
        using the align library '''
    
    # align ref to hyp
    sr = Sequence(ref)
    sh = Sequence(hyp)
    
    v = Vocabulary()
    rEncoded = v.encodeSequence(sr)
    hEncoded = v.encodeSequence(sh)
    
    # Create a scoring and align the sequences using global aligner.
    scoring = SimpleScoring(2, -1)
    aligner = StrictGlobalSequenceAligner(scoring, -100)
    score, encodeds = aligner.align(rEncoded, hEncoded, backtrace=True)

    # Iterate over optimal alignments and print them.
    
    alignment = v.decodeSequenceAlignment(encodeds[0])
    ref_align_raw = [token[0] for token in alignment]
    
    ref_align  = []
    for token in ref_align_raw:
        if token == '-':
            ref_align.append(delete_token)
        else:
            ref_align.append(token)
            
    for i in range(len(hyp) - len(ref_align_raw)):
        ref_align.append(delete_token)
        
    return ref_align
    
def align_ref_long(hyp, ref):
    ''' Aligns a ref to a sausage-aligned hype 
        using the align library '''
    
    # align ref to hyp
    sr = Sequence(ref)
    sh = Sequence(hyp)
    
    v = Vocabulary()
    rEncoded = v.encodeSequence(sr)
    hEncoded = v.encodeSequence(sh)
    
    # Create a scoring and align the sequences using global aligner.
    scoring = SimpleScoring(2, -1)
    aligner = StrictGlobalSequenceAligner(scoring, -2)
    score, encodeds = aligner.align(hEncoded, rEncoded, backtrace=True)
    

    # Iterate over optimal alignments and print them.
    alignment = v.decodeSequenceAlignment(encodeds[0])
    ref_align_raw = [token[0] for token in alignment if token[0] != '-']
    
    ref_align  = []
    for token in ref_align_raw:
        if token == '-':
            ref_align.append(delete_token)
        else:
            ref_align.append(token)
            
    for i in range(len(hyp) - len(ref_align_raw)):
        ref_align.append(delete_token)
        
    return ref_align
    
def score(ref, hyp):
    ''' Scores a hyp based on a ref '''
    
    # Should have the same number of tokens
    if len(ref) != len(hyp):
        raise Exception('Ref and Hyp should have the same number of tokens')
    
    scores = []
    for i in range(len(ref)):
        if ref[i] == hyp[i]:
            scores.append('OK')
        else:
            if ref[i] != delete_token and not ref[i] in vocabulary:
                scores.append('OOV')
            else:
                scores.append('ERROR')
            
    return scores
   
# Custom exceptions    
class ConvergenceError(Exception):        
    def __init__(self, matrix):
        self.matrix = matrix
        
    def __str__(self):
        return 'Convergence failed'
        
class InvalidAlignmentError(Exception):
    def __str__(self):
        return 'Invalid alignment'
        
class InvalidHypError(Exception):
    def __init__(self, sausage, hyp, token):
        self.sausage = sausage
        self.hyp = hyp
        self.token = token
        
    def __str__(self):
        return "Token %s appears in the hyp but doesn't appear in the sausage" % self.token
