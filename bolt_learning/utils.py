import re
from bolt_learning.data import read_output

def get_tokens(s):
    '''Extracts the tokens from a string, lowercases them and removes the star tokens'''

    func = lambda x: not re.match(r'^\*+$', x)
    return filter(func, s.lower().split())

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
