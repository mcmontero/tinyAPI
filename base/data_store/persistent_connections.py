# ----- Info ------------------------------------------------------------------

__author__ = 'Michael Montero <mcmontero@gmail.com>'

# ----- Imports ---------------------------------------------------------------

from tinyAPI.base.config import ConfigManager
from tinyAPI.base.data_store.provider import DataStoreMySQL

import os
import threading

__all__ = [
    'DataStorePersistentConnections'
]

# ----- Public Classes --------------------------------------------------------

class DataStorePersistentConnections(object):
    '''Manages the established persistent connetions to the data store.'''

    __connections = {}
    __wait_timeout = None

    def __init__(self):
        self.__pid = os.getpid()
        self.__wait_timeout = None


    def start(self, connection_name, database_name, log_file=None):
        self.__connection_name = connection_name
        self.__database_name = database_name
        self.__log_file = log_file

        lock = threading.RLock()
        lock.acquire()

        try:
            if ConfigManager.value('data store') == 'mysql':
                mysql = \
                    DataStoreMySQL() \
                        .set_persistent(False) \
                        .select_db(self.__connection_name, self.__database_name)
                record = mysql.one("show variables like '%%wait_timeout%%'")
                if record is None:
                    raise RuntimeError(
                        'could not determine wait_timeout for MySQL')

                self.__wait_timeout = int(record['Value'])
                mysql.close()
            else:
                raise NotImplementedError()
        finally:
            lock.release()


    def get(self):
        if self.__pid not in self.__connections:
            if ConfigManager.value('data store') == 'mysql':
                self.__connections[self.__pid] = \
                    DataStoreMySQL() \
                        .set_wait_timeout(self.__wait_timeout)
            else:
                raise NotImplementedError()

        return self.__connections[self.__pid]
