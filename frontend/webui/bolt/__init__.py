from boltdata import read_output
from prepare_dataset_sxs import get_dataset, get_dataset_linear_regression

# Read the information
names, refs, hyps, sausages, lattices, nbests = read_output()

#Number of refs
ref_num = len(refs)

#Compute the feature vectors
#print "Extracting the dataset for logistic regression"

#bunch_logistic = get_dataset()

#print "Extracting the dataset for linear regression"

#bunch_linear = get_dataset_linear_regression()
