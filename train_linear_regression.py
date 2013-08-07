import prepare_dataset_sxs
from sklearn.linear_model import LinearRegression
from sklearn.cross_validation import train_test_split
from sklearn.metrics import explained_variance_score, r2_score
import pickle
import sys

# If we specify a subset of the data, it will be as a pickle file provided as the second parameter
if len(sys.argv) == 2:
    ids = sys.argv[1]
else: 
    ids = None

data_set = prepare_dataset_sxs.get_dataset_linear_regression(ids)

X_train, X_test, y_train, y_test = train_test_split(data_set.data, data_set.target, test_size=0.25)

model = LinearRegression(normalize=True)
model.fit(X_train, y_train)

y_pred = model.predict(X_test)

print 'Explained variance:', explained_variance_score(y_test, y_pred), 'R^2 score:', r2_score(y_test, y_pred), 'Coefs:', model.coef_, 'Intercept:', model.intercept_

file_name = 'linear_regression.pickle' if ids is None else 'linear_regression_%s.pickle' % ids.split('.')[0]

with open(file_name, 'w') as f:
    pickle.dump(model, f)
