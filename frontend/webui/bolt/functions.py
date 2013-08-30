import pickle
import os
import uuid

def persist_log(log):
    print log
    with create_file() as file:
        pickle.dump(log, file)

def create_file():
    dir = 'logs'
    path = os.path.join('.', dir, str(uuid.uuid4()) + '.log')
    return open(path, 'w+')
