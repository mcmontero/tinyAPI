# ----- Info ------------------------------------------------------------------

__author__ = 'Michael Montero <mcmontero@gmail.com>'

# ----- Imports ---------------------------------------------------------------

from .exception import DataStoreException
from tinyAPI.base.data_store.memcache import Memcache

import time
import tinyAPI.base.context as Context

# ----- Private Classes -------------------------------------------------------

class __DataStoreBase(object):
    '''
    Defines the base level class from which all data store types (like RDBMS)
    should inherit.
    '''

    def __init__(self):
        self._settings = None
        self._db = None
        self._group = None
        self._charset = 'utf8'
        self._memcache = None
        self._memcache_key = None
        self._memcache_ttl = None
        self._ping_interval = 300
        self._inactive_since = time.time()
        self._ordered_dict_cursor = False

        self.persistent = True
        if Context.env_cli() is True:
            self.persistent = False

# ----- Public Classes --------------------------------------------------------

class RDBMSBase(__DataStoreBase):
    '''
    Defines a data store that handles interactions with a RDBMS (MySQL,
    PostgreSQL, etc.).
    '''

    def close(self):
        '''
        Manually close the database connection.
        '''

        raise NotImplementedError

    def commit(self):
        '''
        Manually commit the active transaction.
        '''

        raise NotImplementedError

    def configure(self, settings, db, group):
        '''
        Configure the connection settings.
        '''

        if group not in settings:
            raise DataStoreException(
                'group "{}" not found in settings'
                    .format(group)
            )

        self.close()

        self._settings = settings
        self._db = db
        self._group = group
        return self

    def count(self, sql, binds=tuple()):
        '''
        Given a count(*) query, only return the resultant count.
        '''

        return None

    def create(target, data=tuple(), return_insert_id=False):
        '''
        Create a new record in the RDBMS.
        '''

        return '' if return_insert_id else None

    def delete(target, where=tuple(), binds=tuple()):
        '''
        Delete a record from the RDBMS.
        '''

        return False

    def memcache(self, key, ttl=0):
        '''
        Specify that the result set should be cached in Memcache.
        '''

        self._memcache_key = key
        self._memcache_ttl = ttl
        return self

    def memcache_purge(self):
        '''
        If the data has been cached, purge it.
        '''

        if self._memcache_key is None or Context.env_unit_test():
            return

        if self._memcache is None:
            self._memcache = Memcache()
        self._memcache.purge(self._memcache_key)

    def memcache_retrieve(self):
        '''
        If the data needs to be cached, cache it.
        '''

        if self._memcache_key is None or Context.env_unit_test():
            return None

        if self._memcache is None:
            self._memcache = Memcache()

        return self._memcache.retrieve(self._memcache_key)

    def memcache_store(self, data):
        '''
        If there is data and it should be cached, cache it.
        '''

        if self._memcache_key is None or Context.env_unit_test():
            return

        if self._memcache is None:
            self._memcache = Memcache()

        self._memcache.store(
            self._memcache_key,
            data,
            self._memcache_ttl,
            self._memcache_ttl
        )

    def nth(self, index, sql, binds=tuple()):
        '''
        Return the value at the Nth position of the result set.
        '''

        return None

    def one(self, sql, binds=tuple(), obj=None):
        '''
        Return the first (and only the first) of the result set.
        '''

        record = self.nth(0, sql, binds)
        if obj is None:
            return record

        if record is None:
            raise RuntimeError('no data is present to assign to object')

        for key, value in record.items():
            setattr(obj, key, value)

        return record

    def ordered_dict_cursor(self):
        self._ordered_dict_cursor = True
        return self

    def query(self, query, binds = []):
        '''
        Execute an arbitrary query and return all of the results.
        '''

        return None

    def _reset_memcache(self):
        self._memcache_key = None
        self._memcache_ttl = None

    def rollback(self):
        '''
        Manually rollback the active transaction.
        '''

        raise NotImplementedError

    def set_charset(self, charset):
        '''
        Set the character for the RDBMS.
        '''

        self._charset = charset
        return self

    def set_persistent(self, persistent):
        self.persistent = persistent
        return self

    def should_ping(self):
        if self.persistent is False:
            return False

        should_ping = False
        if (time.time() - self._inactive_since) >= (self._ping_interval - 3):
            should_ping = True

        self._inactive_since = time.time()

        return should_ping
