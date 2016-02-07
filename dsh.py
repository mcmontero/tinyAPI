# ----- Info ------------------------------------------------------------------

__author__ = 'Michael Montero <mcmontero@gmail.com>'

# ----- Imports ---------------------------------------------------------------

from tinyAPI.base.data_store.provider import DataStoreNOOP
from tinyAPI.base.data_store.provider import DataStoreProvider

import tinyAPI

__all__ = [
    'dsh'
]

# ----- Instructions ----------------------------------------------------------

class __DSH(object):

    def __init__(self):
        self.__provider = None


    def __call__(self):
        return \
            (self.__provider
                if self.__provider is not None else
             DataStoreNOOP())


    def select_db(self, connection, db, persistent=True):
        self.__provider = \
            DataStoreProvider() \
                .get_data_store_handle(
                    connection,
                    db,
                    tinyAPI.env_cli() is not True and persistent
                )
        return self

dsh = __DSH()
