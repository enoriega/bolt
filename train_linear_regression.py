import prepare_dataset_sxs
from sklearn.linear_model import LinearRegression
from sklearn.cross_validation import train_test_split
from sklearn.metrics import explained_variance_score, r2_score
import pickle

data_set = prepare_dataset_sxs.get_dataset_linear_regression()

X_train, X_test, y_train, y_test = train_test_split(data_set.data, data_set.target, test_size=0.25)

model = LinearRegression(normalize=True)
model.fit(X_train, y_train)

y_pred = model.predict(X_test)

print 'Explained variance:', explained_variance_score(y_test, y_pred), 'R2 score:', r2_score(y_test, y_pred)

with open('linear_regression.pickle', 'w') as f:
	pickle.dump(model, f)
