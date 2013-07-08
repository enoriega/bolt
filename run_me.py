import boltdata
from sausages import Sausage

# IMPORTANT
# Set this variable to the corresponding path
OUTPUT_DIR = '../output'

# Load all the info into memory
names, refs, hyps, sausages, lattices, nbests = boltdata.read_output(OUTPUT_DIR)


# Select a sausage and its nbests list
# their indices match
sfile = sausages[0]
nfile = nbests[0]
id = names[0]

# Create a Sausage instance
sausage = Sausage.from_file(sfile, nfile, id)
nbests = sausage.aligned_nbests()

