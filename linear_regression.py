from logistic_regression import error_names, error_hyps
import pickle
from sausages import Sausage, read_nbest, read_word_scores
from boltdata import read_output
from sausage_aligner import delete_token
from prepare_dataset_sxs import get_tokens
from sklearn.preprocessing import scale
import numpy as np

threshold = 4

with open('linear_regression.pickle', 'r') as f:
    model = pickle.load(f)

X = []
names = []

for name, ref, hyp, sausage, lattice, nbest in zip(*read_output()):
	if name in error_names:
		names.append(name)
		s = Sausage.from_file(sausage)
		# Create feature vector
		ascore, lscore, _ = read_nbest(nbest)[0]
		hyp = get_tokens(hyp)
		try:
            		aligned_hyp, score = s.align_hyp(' '.join(hyp))
        	except:
            		continue    
        	v = [lscore, score, len([t for t in aligned_hyp if t == delete_token]), len(hyp), 1.0/float(len(hyp))]
		X.append(v)

X = scale(np.array(X))

y_pred = model.predict(X)

names = np.char.array(names)

fixable = names[y_pred <= threshold]
unfixable = names[y_pred > threshold]

