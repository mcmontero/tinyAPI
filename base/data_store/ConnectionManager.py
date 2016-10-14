# ----- Info ------------------------------------------------------------------

__author__ = 'Michael Montero <mcmontero@gmail.com>'

# ----- Imports ---------------------------------------------------------------

from tinyAPI.base.config import ConfigManager
from tinyAPI.base.data_store.MySQL import MySQL
from tinyAPI.base.data_store.PostgreSQL import PostgreSQL

import builtins
import os
import threading

# ----- Thread Local Data -----------------------------------------------------

_thread_local_data = threading.local()

# ----- Public Classes --------------------------------------------------------

class ConnectionManager(object):
    '''
    Manages connectivity and persistence for data store connections.
    '''

    __persistent = {}

    def __init__(self):
        self.pid = os.getpid()
        self.config = ConfigManager.value('data store config')

    def acquire(self, server, db, group, persistent=False):
        if server not in self.__persistent:
            self.__persistent[server] = {}

        if not hasattr(_thread_local_data, server):
            if persistent is True:
                if self.pid not in self.__persistent[server]:
                    self.__persistent[server][self.pid] = \
                        self.__get_data_store_handle(server)

                dsh = self.__persistent[server][self.pid]
                setattr(_thread_local_data, server, dsh)
            else:
                dsh = \
                    self.__get_data_store_handle(server) \
                        .set_persistent(False)
                setattr(_thread_local_data, server, dsh)
        else:
            dsh = getattr(_thread_local_data, server)

        _configure_dsh_builtins(dsh)

        return dsh.configure(self.config[server], db, group)

    def __get_data_store_handle(self, server):
        if server not in self.config:
            raise RuntimeError(
                'server "{}" is not configured in "data store config"'
                    .format(server)
            )

        if 'type' not in self.config[server]:
            raise RuntimeError(
                'data store configuration for "{}" is missing "type"'
                    .format(server)
            )

        if self.config[server]['type'] == 'mysql':
            return MySQL()
        elif self.config[server]['type'] == 'postgresql':
            return PostgreSQL()
        else:
            raise RuntimeError(
                'unrecognized data store type "{}"'
                    .format(self.config[server]['type'])
            )

# ----- Protected Functions ---------------------------------------------------

def _configure_dsh_builtins(dsh):
    builtins._c = dsh.count
    builtins._cr = dsh.create
    builtins._close = dsh.close
    builtins._commit = dsh.commit
    builtins._dsh = dsh
    builtins._o = dsh.one
    builtins._q = dsh.query
    builtins._rollback = dsh.rollback

# ----- Intstructions ---------------------------------------------------------

builtins._dscm = ConnectionManager()
builtins._ds = builtins._dscm.acquire
