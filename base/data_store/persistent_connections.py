# ----- Info ------------------------------------------------------------------

__author__ = 'Michael Montero <mcmontero@gmail.com>'

# ----- Imports ---------------------------------------------------------------

from tinyAPI.base.data_store.provider import DataStoreProvider

import os
import tinyAPI

__all__ = [
    'DataStorePersistentConnections'
]

# ----- Public Classes --------------------------------------------------------

def get_connection():
    return DataStorePersistentConnections().get_connection()


class DataStorePersistentConnections(object):
    '''Configures the system for persistent connections.'''

    __connections = {}

    def __init__(self):
        self.pid = os.getpid()
        if self.pid not in self.__connections:
            self.__connections[self.pid] = \
                DataStoreProvider().get_data_store_handle()
            self.__connections[self.pid].select_db('master', 'core')
            self.__connections[self.pid].one('select 1 from dual')


    def get_connection(self):
        return self.__connections[self.pid]
