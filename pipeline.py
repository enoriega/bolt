from prepare_dataset_sxs import get_dataset, get_dataset_linear_regression
import pickle

print 'Loading classifiers ...'
with open('logistic_regression.pickle', 'rb') as f:
    c1 = pickle.load(f)

with open('linear_regression_ok_names.pickle', 'rb') as f:
    reg_ok = pickle.load(f)

with open('linear_regression_error_names.pickle', 'rb') as f:
    reg_err = pickle.load(f)

print 'Loading dataset ...'
X = get_dataset().data

print 'Classifying data ...'
y_pred = c1.predict(X)

err_idx = y_pred.astype(bool)
print 'OK:', X[~err_idx].shape[0], 'Error:', X[err_idx].shape[0]

print 'Loading dataset again ...'
bunch = get_dataset_linear_regression()
X = bunch.data

X_ok = X[~err_idx]
X_err = X[err_idx]


print 'Regression on X_ok ...'
y_pred_ok = reg_ok.predict(X_ok)

print 'Regression on X_err ...'
y_pred_err = reg_err.predict(X_err)

print 'Pred ok > 2:', y_pred_ok[y_pred_ok > 2].shape[0], 'Pred ok <= 2:', y_pred_ok[y_pred_ok <= 2].shape[0]

print y_pred_ok


print 'Pred err > 4:', y_pred_err[y_pred_err > 4].shape[0], 'Pred err <= 4:', y_pred_err[y_pred_err <= 4].shape[0]

print 'Mean WER pred ok > 2:', bunch.target[y_pred_ok > 2].mean(), 'Mean WER pred ok <= 2:', bunch.target[y_pred_ok <=2].mean()
print 'Mean WER pred err > 4:', bunch.target[y_pred_err > 4].mean(), 'Mean WER pred err <= 4:', bunch.target[y_pred_err <=4].mean()
