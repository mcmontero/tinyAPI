# ----- Info ------------------------------------------------------------------

__author__ = 'Michael Montero <mcmontero@gmail.com>'

# ----- Imports ---------------------------------------------------------------

from tinyAPI.base.data_store.provider import DataStoreProvider

__all__ = [
    'dsh'
]

# ----- Public Functions  -----------------------------------------------------

def dsh():
    '''Returns a usable handle to the configured data store.'''
    return DataStoreProvider().get_data_store_handle()
