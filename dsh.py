# ----- Info ------------------------------------------------------------------

__author__ = 'Michael Montero <mcmontero@gmail.com>'

# ----- Imports ---------------------------------------------------------------

from tinyAPI.base.data_store.provider import DataStoreProvider

import tinyAPI

__all__ = [
    'dsh'
]

# ----- Private Classes -------------------------------------------------------

class UnitTestNullDSH(object):
    '''
    Supports unit test cases that do not perform transactional data store
    operations but attempt to close or rollback transactions.
    '''

    def close(self):
        pass


    def rollback(self, ignore_exceptions=True):
        pass

# ----- Instructions ----------------------------------------------------------

class __DSH(object):

    def __init__(self):
        self.__provider = None
        self.__unit_test_null_dsh = UnitTestNullDSH()

    def __call__(self):
        if self.__provider is None:
            if tinyAPI.env_unit_test() is True:
                return self.__unit_test_null_dsh
            else:
                raise RuntimeError('data store handle has not been selected')

        return self.__provider


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
