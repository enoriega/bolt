import prepare_dataset_sxs
from sklearn.linear_model import LinearRegression
from sklearn.cross_validation import train_test_split
from sklearn.metrics import explained_variance_score, r2_score
import pickle
import sys
from bolt_learning import CLASSIFICATOR_FILE_NAME, OK_REGRESSION_FILE_NAME, ERROR_REGRESSION_FILE_NAME
from bolt_learning.features import get_classification_dataset, get_regression_dataset

with open(CLASSIFICATOR_FILE_NAME, 'rb') as f:
    classificator = pickle.load(f)

c_dataset = get_classification_dataset()

X = c_dataset.data
y_pred = classificator.predict(X)
err_idx = y_pred.astype(bool)

ids_ok, ids_err = [i for i in range(X.shape[0]) if err_idx[i] == False], [i for i in range(X.shape[0] if err_idx[i] == True]

for ids, file_name in zip([ids_ok, ids_err], [OK_REGRESSION_FILE_NAME, ERROR_REGRESSION_FILE_NAME]):

    data_set = get_regression_dataset(ids)

    X_train, X_test, y_train, y_test = train_test_split(data_set.data, data_set.target, test_size=0.25)

    model = LinearRegression(normalize=True)
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)

    print 'Explained variance:', explained_variance_score(y_test, y_pred), 'R^2 score:', r2_score(y_test, y_pred), 'Coefs:', model.coef_, 'Intercept:', model.intercept_

    with open(file_name, 'w') as f:
        pickle.dump(model, f)
