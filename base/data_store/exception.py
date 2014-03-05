'''exception.py -- Defines named exceptions for Data Store operations.'''

__author__ = 'Michael Montero <mcmontero@gmail.com>'

# ----- Public Classes -------------------------------------------------------

class DataStoreException(Exception):
    '''Named exception identifying an issue specifically with an underlying
       data store.'''

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class DataStoreDuplicateKeyException(DataStoreException):
    '''Named exception identifying when a duplicate key is being added to a
       RDBMS.'''

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)

__all__ = ['DataStoreDuplicateKeyException', 'DataStoreException']
