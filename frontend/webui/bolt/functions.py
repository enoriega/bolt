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

def close_log_entry(*entry_names):
    '''Decorates a "view"(controller) to delete previous entries of the log in case that
       the user uses the navigation keys (that way we avoid duplicate entries)'''
    def wrapper(function):   
        def inner(*args, **kwargs):

            request = args[0] # recover the request

            #Recover the log
            if 'log' in request.session:
                log = request.session['log']

            #Now traverse the log searching for a previous entry with the same
            #entry name. In case that it's found, slice the log to delete subsequent
            #records
            for i in reversed(range(len(log))):
                if log[i]['name'] in entry_names:
                    log = log[:i]
                    break

            return function(*args, **kwargs)
        return inner
    return wrapper
