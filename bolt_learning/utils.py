import re

def get_tokens(s):
    '''Extracts the tokens from a string, lowercases them and removes the star tokens'''

    func = lambda x: not re.match(r'^\*+$', x)
    return filter(func, s.lower().split())
