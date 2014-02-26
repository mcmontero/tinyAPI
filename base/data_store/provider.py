'''provider.py -- Data store providers are mechanism for talking to databases,
   document stores, caching sub-systems, etc. that are configured into tinyAPI.
   They are designed to be less verbose (and configuration driven where
   possible) to make getting and setting data easy and portable.'''

__author__ = 'Michael Montero <mcmontero@gmail.com>'

# ----- Imports --------------------------------------------------------------

from .exception import DataStoreException
from tinyAPI.base.config import ConfigManager
from tinyAPI.base.data_store.memcache import Memcache
from tinyAPI.base.singleton import Singleton

# ----- Private Classes ------------------------------------------------------

class __DataStoreBase(object):
    '''Defines the base level class from which all data store types (like
       RDBMS) should inherit.'''

    _connection_name = None
    _charset = None
    _db = None
    _memcache_key = None
    _memcache_ttl = None

# ----- Public Classes -------------------------------------------------------

class RDBMSBase(__DataStoreBase):
    '''Defines a data store that handles interactions with a RDBMS (MySQL,
       PostgreSQL, etc.).'''

    '''Manually commit the active transaction.'''
    def commit():
        raise NotImplementedError

    '''Create a new record in the RDBMS.'''
    def create(target, data=tuple(), return_insert_id=False):
        return '' if return_insert_id else None

    '''Delete a record from the RDBMS.'''
    def delete(target, where=tuple(), binds=tuple()):
        return False

    '''Specify that the result set should be cached in Memcache.'''
    def memcache(key, ttl=0):
        self._memcache_key = key
        self._memcache_ttl = ttl

    '''If the data has been cached, purge it.'''
    def memcache_purge():
        if self._memcache_key == '':
            return
        Memcache().purge(self._memcache_key)

    '''If the data needs to be cached, cache it.'''
    def memcache_retrieve():
        if self._memcache_key == '':
            return None
        Memcache().retrieve(self._memcache_key)

    '''If there is data and it should be cached, cache it.'''
    def memcache_store(data):
        if self._memcache_key == '':
            return
        Memcache.store(self._memcache_key, data, self._memcache_ttl)

    '''Execute an arbitrary query.'''
    def query(caller, query, binds = []):
        return None

    '''Select data from the RDBMS.'''
    def retrieve(target, cols=tuple(), where=tuple(), binds=tuple()):
        return None

    '''Manually rollback the active transaction.'''
    def rollback():
        raise NotImplementedError

    '''Select which connection and database schema to use.'''
    def select_db(connection, db):
        self._connection_name = connection
        self._db = db

    '''Set the character for the RDBMS.'''
    def set_charset(charset):
        self._charset = charset

    '''Update a record in the RDBMS.'''
    def update(target, data=tuple(), where=tuple(), binds=tuple()):
        return False


class DataStoreMySQL(RDBMSBase):
    '''Manages interactions with configured MySQL servers.'''

    __mysql = None

    def commit(self):
        if self.__mysql is None:
            raise DataStoreException(
                'transaction cannot be committed becase a database connection '
                + 'has not been established yet')
        else:
            self.__mysql.commit()


class DataStoreProvider(metaclass=Singleton):
    '''Defines the main mechanism for retrieving a handle to a configured data
       store.'''

    __dsh = None

    '''Get the active data store handle against which to execute operations.'''
    def get_data_store_handle(self):
        if ConfigManager.value('data store') == 'mysql':
            if self.__dsh is None:
                self.__dsh = DataStoreMySQL()
            return self.__dsh
        else:
            raise DataStoreException(
                'configured data store is not currently supported')

__all__ = ['DataStoreMySQL', 'DataStoreProvider', 'RDBMSBase']
