from bolt_learning.data import read_output
import pickle
# Read the information
names, refs, hyps, sausages, lattices, nbests, wavs = read_output()

#Number of refs
ref_num = len(refs)

with open('ok_index.pickle', 'rb') as f:
    ok_index = pickle.load(f)

with open('error_index.pickle', 'rb') as f:
    error_index = pickle.load(f)

with open('m4_index.pickle', 'rb') as f:
    m4_index = pickle.load(f)


with open('l4_index.pickle', 'rb') as f:
    l4_index = pickle.load(f)

index = range(ref_num)

# This variable is an on/off switch for the models
intelligence = False
