# ----- Info ------------------------------------------------------------------

__author__ = 'Michael Montero <mcmontero@gmail.com>'

# ----- Imports ---------------------------------------------------------------

from tinyAPI.base.config import ConfigManager
from tinyAPI.base.data_store.provider import DataStoreMySQL

import logging
import random
import re
import threading
import time
import tinyAPI

__all__ = [
    'DataStoreConnectionPool'
]

# ----- Thread Local Data -----------------------------------------------------

_thread_local_data = threading.local()
_thread_local_data.connection_pools = {}

# ----- Public Classes --------------------------------------------------------

class _DataStorePooledMySQLConnection(object):
    '''Represents a single, pooled MySQL connection.'''

    def __init__(self, index, handle):
        self.__handle = handle
        self.__active_since = None
        self.__inactive_since = time.time()
        self.requests = 0
        self.hits = 0
        self.timeout = None
        self.connected = False

        self.__handle.is_pooled = True
        self.__handle.pool_index = index


    def get(self):
        if self.__active_since is not None:
            raise RuntimeError(
                'cannot get handle because it is already active')

        self.requests += 1
        self.__maintain_connection()

        self.__active_since = time.time()
        self.__inactive_since = None

        return self.__handle


    def __maintain_connection(self):
        if self.connected is False:
            self.__handle.connect()
            self.connected = True
        else:
            if self.__timeout is None:
                raise RuntimeError(
                    'cannot maintain connection without timeout value')

            if int(time.time() - self.__inactive_since) >= (self.__timeout - 3):
                self.__handle.close()
                self.__handle.connect()
                self.connected = True
            else:
                self.hits += 1


    def release(self):
        self.__inactive_since = time.time()
        self.__active_since = None
        return self


    def set_timeout(self, timeout):
        self.__timeout = timeout
        return self


class DataStoreConnectionPool(object):
    '''Manages a pool of connections to the selected data store.'''

    def __init__(self):
        self.__started = False
        self.__pool = {}
        self.__avail = []
        self.__timeout = None
        self.__log_file = None
        self.__requests = 0
        self.__hits = 0
        self.name = None
        self.connection_name = None
        self.database_name = None
        self.size = None


    def __del__(self):
        if self.__started is True:
            self.__unavail = []
            for index, pooled_connection in self.__pool.items():
                pooled_connection = None

            self.__pool = {}
            self.__started = False


    @staticmethod
    def get(name):
        return (_thread_local_data.connection_pools[name]
                    if name in _thread_local_data.connection_pools else
                None)


    def get_dsh(self):
        if len(self.__avail) == 0:
            raise RuntimeError(
                'no connections available; consider resizing pool')

        self.__semaphore.acquire()

        if tinyAPI.env_unit_test() is True:
            index = 0
        else:
            index = self.__avail[0]

        del self.__avail[0]

        self.__semaphore.release()

        if tinyAPI.env_unit_test() is False and \
           self.__log_file is not None and \
           random.randint(1, 50) == 1:
            logging.basicConfig(filename = self.__log_file)

            lines = [
                "\n----- tinyAPI Connection Pool Stats (start) ----------------"
            ]

            if self.__timeout is not None and self.__timeout <= 120:
                lines.append("MySQL wait_timeout value is too log!")

            requests = 0
            hits = 0
            for index, pooled_connection in self.__pool.items():
                requests += pooled_connection.requests
                hits += pooled_connection.hits

                lines.append(
                    'Connection #'+ str(index) + ': '
                    + 'requests = ' + '{0:,}'.format(requests) + ', '
                    + 'hits = ' + '{0:,}'.format(hits))

            if requests > 0:
                lines.append(
                    "Pool hit ratio: " + str((hits / requests) * 100) + "%")
            else:
                lines.append(
                    "Pool hit ratio is not available yet.")

            lines.append(
                "----- tinyAPI Connection Pool Stats (stop) -----------------")

            logging.critical("\n".join(lines))
            logging.shutdown()

        return self.__pool[index].get()


    def release_dsh(self, conn):
        if conn.is_pooled is False or conn.pool_index is None:
            raise RuntimeError(
                'connection was not properly retrieved from pool')

        if tinyAPI.env_unit_test() is False:
            conn.rollback(True)
        tinyAPI.release_dsh()

        self.__pool[conn.pool_index].release()
        self.__avail.append(conn.pool_index)
        return self


    def set_log_file(self, log_file):
        self.__log_file = log_file
        return self


    def start(self, name, connection_name, database_name, size, is_default):
        if self.__started is True:
            raise RuntimeError(
                'cannot start connection pool because it is already running')

        if not re.search('^[a-z_]+$', name):
            raise RuntimeError(
                'name can only consistent of lowercase letters and underscores')

        if size <= 0:
            raise RuntimeError('size must be greater than or equal to 1')

        self.__semaphore = threading.BoundedSemaphore(size)
        self.name = name
        self.connection_name = connection_name
        self.database_name = database_name
        self.size = size

        if ConfigManager.value('data store') == 'mysql':
            for i in range(self.size):
                self.__pool[i] = \
                    _DataStorePooledMySQLConnection(
                        i,
                        DataStoreMySQL()
                            .select_db(
                                self.connection_name,
                                self.database_name))
                self.__pool[i].release()
                self.__avail.append(i)

            dsh = self.get_dsh()

            record = dsh.one("show variables like 'wait_timeout'")
            if record is None:
                raise RuntimeError(
                    'cannot determine wait timeout value for MySQL')

            self.__timeout = int(record['Value'])

            self.release_dsh(dsh)

            for index, pooled_connection in self.__pool.items():
                pooled_connection.set_timeout(self.__timeout)
        else:
            raise NotImplementedError()

        if is_default is True:
            self.name = 'default'

        _thread_local_data.connection_pools[self.name] = self

        self.__started = True

        return self
