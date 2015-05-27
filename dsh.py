# ----- Info ------------------------------------------------------------------

__author__ = 'Michael Montero <mcmontero@gmail.com>'

# ----- Imports ---------------------------------------------------------------

from tinyAPI.base.data_store.provider import DataStoreProvider

import tinyAPI

__all__ = [
    'dsh'
]

# ----- Public Functions  -----------------------------------------------------

def dsh(persistent=True):
    '''Returns a usable handle to the configured data store.'''
    return DataStoreProvider().get_data_store_handle(
            tinyAPI.env_cli() is not True and persistent)
