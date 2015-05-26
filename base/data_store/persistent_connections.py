# ----- Info ------------------------------------------------------------------

__author__ = 'Michael Montero <mcmontero@gmail.com>'

# ----- Imports ---------------------------------------------------------------

from tinyAPI.base.data_store.provider import DataStoreProvider

import tinyAPI

__all__ = [
    'DataStorePersistentConnections'
]

# ----- Public Classes --------------------------------------------------------

class DataStorePersistentConnections(object):
    '''Configures the system for persistent connections.'''

    def __init__(self):
        self.__dsh = DataStoreProvider().get_data_store_handle()
        tinyAPI.set_dsh(self.__dsh)

