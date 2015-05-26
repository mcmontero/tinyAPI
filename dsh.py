# ----- Info ------------------------------------------------------------------

__author__ = 'Michael Montero <mcmontero@gmail.com>'

# ----- Imports ---------------------------------------------------------------

from tinyAPI.base.data_store.persistent_connections \
    import DataStorePersistentConnections
from tinyAPI.base.data_store.provider \
    import DataStoreProvider

import threading
import tinyAPI

__all__ = [
    'dsh'
]

# ----- Thread Local Data -----------------------------------------------------

_thread_local_data = threading.local()

# ----- Public Functions  -----------------------------------------------------

def dsh():
    '''Returns a usable handle to the configured data store.'''
    if tinyAPI.env_cli() is False:
        return DataStorePersistentConnections().get()
    else:
        if not hasattr(_thread_local_data, 'dsh'):
            _thread_local_data.dsh = \
                DataStoreProvider().get_data_store_handle()

        return _thread_local_data.dsh
