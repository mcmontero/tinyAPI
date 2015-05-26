# ----- Info ------------------------------------------------------------------

__author__ = 'Michael Montero <mcmontero@gmail.com>'

# ----- Imports ---------------------------------------------------------------

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
        _thread_local_data.dsh = DataStoreProvider().get_data_store_handle()

    return _thread_local_data.dsh


def set_dsh(handle):
    _thread_local_data.dsh = handle
