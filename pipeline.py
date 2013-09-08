import pickle
from bolt_learning import CLASSIFICATOR_FILE_NAME, OK_REGRESSION_FILE_NAME, ERROR_REGRESSION_FILE_NAME
from bolt_learning.features import get_classification_dataset, get_regression_dataset

# Load the models
with open(CLASSIFICATOR_FILE_NAME, 'rb') as f:
    classificator = pickle.load(f)

with open(OK_REGRESSION_FILE_NAME, 'rb') as f:
    ok_regression = pickle.load(f)


with open(ERROR_REGRESSION_FILE_NAME, 'rb') as f:
    error_regression = pickle.load(f)

# Perform classification
print 'Loading classificarion dataset ...'
X = get_classification_dataset().data

print 'Classifying data ...'
y_pred = classificator.predict(X)

err_idx = y_pred.astype(bool)
print 'OK:', X[~err_idx].shape[0], 'Error:', X[err_idx].shape[0]

ids_ok, ids_err = [i for i in range(X.shape[0]) if err_idx[i] == False], [i for i in range(X.shape[0]) if err_idx[i] == True]

print 'Loading regression datasets ...'
X_ok = get_regression_dataset(ids_ok)
X_err = get_regression_dataset(ids_err)


print 'Regression on X_ok ...'
y_pred_ok = ok_regression.predict(X_ok.data)

print 'Regression on X_err ...'
y_pred_err = error_regression.predict(X_err.data)

print 'Pred ok > 2:', y_pred_ok[y_pred_ok > 2].shape[0], 'Pred ok <= 2:', y_pred_ok[y_pred_ok <= 2].shape[0]


print 'Pred err > 4:', y_pred_err[y_pred_err > 4].shape[0], 'Pred err <= 4:', y_pred_err[y_pred_err <= 4].shape[0]

print 'Mean WER pred ok > 2:', X_ok.target[y_pred_ok > 2].mean(), 'Mean WER pred ok <= 2:', X_ok.target[y_pred_ok <=2].mean()
print 'Mean WER pred err > 4:', X_err.target[y_pred_err > 4].mean(), 'Mean WER pred err <= 4:', X_err.target[y_pred_err <=4].mean()

#print 'No. of refs in nbest for pred err <= 4:', get_counts(5, bunch.names[y_pred_err <=4]), 'out of', y_pred_err[y_pred_err <= 4].shape[0] 
