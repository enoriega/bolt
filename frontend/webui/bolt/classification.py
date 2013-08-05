import bolt
from prepare_dataset_sxs import *
from sausages import Sausage
import pickle
import numpy as np
import os

base_path = os.path.dirname(os.path.abspath(__file__))

with open(os.path.join(base_path, 'logistic_regression.pickle'), 'rb') as f:
    logistic_classifier = pickle.load(f)

with open(os.path.join(base_path,'linear_regression.pickle'), 'rb') as f:
    linear_regression = pickle.load(f)

def create_feature_vector_logistic(hyp, sausage, nbest):
    data = []
    
    hyp = get_tokens(hyp)
    aligned_hyp, score = sausage.align_hyp(' '.join(hyp))

    ascore, lscore, _ = read_nbest(nbest)[0]
    v = feature_vectors(hyp, aligned_hyp, sausage, score, ascore, lscore)
    data.append(v)
    #data = scale(np.array(data))
    data = np.array(data)

    return data

def ok_or_error(vector):
    X = logistic_classifier.predict(vector)
    
    return list(X)

def create_feature_vector_linear(hyp, sausage, nbest):
    data = []
    hyp = get_tokens(hyp)
    aligned_hyp, score = sausage.align_hyp(' '.join(hyp))
    ascore, lscor, _ = read_nbest(nbest)[0]
    v = [lscore, score, len([t for t in aligned_hyp if t == delete_token]), len(hyp), 1.0/float(len(hyp))]
    data.append(v)
    data = np.array(data)

    return data

def predicted_wer(vector):
    X = linear_regression.predict(vector)

    return list(X)
