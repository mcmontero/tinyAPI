# ----- Info ------------------------------------------------------------------

__author__ = 'Michael Montero <mcmontero@gmail.com>'

# ----- Imports ---------------------------------------------------------------

from tinyAPI.base.exception import tinyAPIException

__all__ = [
    'DataStoreDuplicateKeyException',
    'DataStoreException'
]

# ----- Public Classes --------------------------------------------------------

class DataStoreException(tinyAPIException):
    '''Named exception identifying an issue specifically with an underlying
       data store.'''
    pass


class DataStoreDuplicateKeyException(DataStoreException):
    '''Named exception identifying when a duplicate key is being added to a
       RDBMS.'''
    pass
