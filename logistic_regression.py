from sklearn.linear_model import LogisticRegression
import prepare_dataset_sxs as pd
import pickle


with open('lr.pickle', 'r') as f:
	model = pickle.load(f)

data_set = pd.get_dataset()

y_pred = model.predict(data_set.data)

error_names = data_set.names[y_pred.astype(bool)]
ok_names = data_set.names[~y_pred.astype(bool)]
error_hyps = data_set.hyps[y_pred.astype(bool)]
ok_hyps = data_set.hyps[~y_pred.astype(bool)]

if __name__ == '__main__':
	print error_names, ok_names, error_hyps, ok_hyps
