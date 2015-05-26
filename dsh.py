# ----- Info ------------------------------------------------------------------

__author__ = 'Michael Montero <mcmontero@gmail.com>'

# ----- Imports ---------------------------------------------------------------

from tinyAPI.base.data_store.connection_pool import DataStoreConnectionPool
from tinyAPI.base.data_store.provider import DataStoreProvider

import threading

__all__ = [
    'dsh'
]

# ----- Thread Local Data -----------------------------------------------------

_thread_local_data = threading.local()

# ----- Public Functions  -----------------------------------------------------

def dsh():
    '''Returns a usable handle to the configured data store.'''
    if 'dsh' not in _thread_local_data.__dict__:
        connection_pool = DataStoreConnectionPool.get('default')
        if connection_pool is not None:
            dsh = connection_pool.get_dsh()
        else:
            dsh = DataStoreProvider().get_data_store_handle()

        _thread_local_data.dsh = dsh

    return _thread_local_data.dsh


def release_dsh():
    if 'dsh' in _thread_local_data.__dict__:
        del _thread_local_data.dsh
