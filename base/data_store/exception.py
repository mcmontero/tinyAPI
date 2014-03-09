'''exception.py -- Defines named exceptions for Data Store operations.'''

__author__ = 'Michael Montero <mcmontero@gmail.com>'

# ----- Import ---------------------------------------------------------------

from tinyAPI.base.exception import tinyAPIException

# ----- Public Classes -------------------------------------------------------

class DataStoreException(tinyAPIException):
    '''Named exception identifying an issue specifically with an underlying
       data store.'''
    pass


class DataStoreDuplicateKeyException(DataStoreException):
    '''Named exception identifying when a duplicate key is being added to a
       RDBMS.'''
    pass

__all__ = ['DataStoreDuplicateKeyException', 'DataStoreException']
