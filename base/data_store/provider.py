'''provider.py -- Data store providers are mechanism for talking to databases,
   document stores, caching sub-systems, etc. that are configured into tinyAPI.
   They are designed to be less verbose (and configuration driven where
   possible) to make getting and setting data easy and portable.'''

__author__ = 'Michael Montero <mcmontero@gmail.com>'

# ----- Imports ---------------------------------------------------------------

from .exception import DataStoreException, DataStoreDuplicateKeyException
from .mysql import MySQLCursorDict
from mysql.connector import errorcode
from tinyAPI.base.config import ConfigManager
from tinyAPI.base.data_store.memcache import Memcache
from tinyAPI.base.singleton import Singleton
import mysql.connector
import re

# ----- Private Classes -------------------------------------------------------

class __DataStoreBase(object):
    '''Defines the base level class from which all data store types (like
       RDBMS) should inherit.'''

    def __init__(self):
        self._connection_name = None
        self._charset = 'utf8'
        self._db_name = None
        self._memcache_key = None
        self._memcache_ttl = None

# ----- Public Classes --------------------------------------------------------

class RDBMSBase(__DataStoreBase):
    '''Defines a data store that handles interactions with a RDBMS (MySQL,
       PostgreSQL, etc.).'''

    def commit():
        '''Manually commit the active transaction.'''
        raise NotImplementedError

    def count(self, sql, binds=tuple()):
        '''Given a count(*) query, only return the resultant count.'''
        return None

    def create(target, data=tuple(), return_insert_id=False):
        '''Create a new record in the RDBMS.'''
        return '' if return_insert_id else None

    def delete(target, where=tuple(), binds=tuple()):
        '''Delete a record from the RDBMS.'''
        return False

    def memcache(self, key, ttl=0):
        '''Specify that the result set should be cached in Memcache.'''
        self._memcache_key = key
        self._memcache_ttl = ttl
        return self

    def memcache_purge(self):
        '''If the data has been cached, purge it.'''
        if self._memcache_key is None:
            return
        Memcache().purge(self._memcache_key)

    def memcache_retrieve(self):
        '''If the data needs to be cached, cache it.'''
        if self._memcache_key is None:
            return None
        return Memcache().retrieve(self._memcache_key)

    def memcache_store(self, data):
        '''If there is data and it should be cached, cache it.'''
        if self._memcache_key is None:
            return
        Memcache.store(self._memcache_key, data, self._memcache_ttl)

    def nth(self, index, sql, binds=tuple()):
        '''Return the value at the Nth position of the result set.'''
        return None

    def query(self, query, binds = []):
        '''Execute an arbitrary query and return all of the results.'''
        return None

    def rollback():
        '''Manually rollback the active transaction.'''
        raise NotImplementedError

    def select_db(self, connection, db):
        '''Select which connection and database schema to use.'''
        if self._connection_name != connection or self._db_name != db:
            self.__mysql = None

        self._connection_name = connection
        self._db_name = db
        return self

    def set_charset(charset):
        '''Set the character for the RDBMS.'''
        self._charset = charset
        return self


class DataStoreMySQL(RDBMSBase):
    '''Manages interactions with configured MySQL servers.'''

    def __init__(self):
        super(DataStoreMySQL, self).__init__()

        self.__mysql = None

    def commit(self):
        '''Commit the active transaction.'''
        if self.__mysql is None:
            raise DataStoreException(
                'transaction cannot be committed becase a database connection '
                + 'has not been established yet')
        else:
            self.__mysql.commit()

    def __connect(self):
        '''Perform the tasks required for connecting to the database.'''
        if self.__mysql is not None:
            return

        if self._connection_name is None:
            raise DataStoreException(
                'cannot connect to MySQL because a connection name has not '
                + 'been provided')

        connection_data = ConfigManager().value('mysql connection data')
        if self._connection_name not in connection_data:
                raise DataStoreException(
                    'the MySQL connection name you provided is invalid')

        if self._db_name is None:
            raise DataStoreException(
                'cannot connection to MySQL because no database name was '
                + 'selected')

        self.__mysql = mysql.connector.connect(
            user=connection_data[self._connection_name][1],
            password=connection_data[self._connection_name][2],
            host=connection_data[self._connection_name][0],
            database=self._db_name,
            charset=self._charset)

    def __convert_to_prepared(self, separator, data=tuple()):
        binds = self.__get_binds(data)

        clause = []
        for index, key in enumerate(data.keys()):
            assignment = ''
            assignment += key + ' = '
            assignment += binds[index]
            clause.append(assignment)

        return separator.join(clause)

    def count(self, sql, binds=tuple()):
        return list(self.nth(0, sql, binds).values())[0]

    def create(self, target, data=tuple(), return_insert_id=True):
        if len(data) == 0:
            return None

        keys = list(data.keys())
        binds = self.__get_binds(data)
        vals = list(data.values())

        sql  = 'insert into ' + target + '('
        sql += ', '.join(keys)
        sql += ')'
        sql += ' values ('
        sql += ', '.join(binds)
        sql += ')'

        self.__connect()

        cursor = self.__get_cursor()

        try:
            cursor.execute(sql, vals)
        except mysql.connector.errors.IntegrityError as e:
            if e.errno == 1062:
                raise DataStoreDuplicateKeyException(e.msg)
            else:
                raise

        id = None
        if return_insert_id:
            id = cursor.getlastrowid()

        cursor.close()

        return id

    def delete(self, target, data=tuple()):
        sql = 'delete from ' + target

        binds = None
        if len(data) > 0:
            sql += ' where ' + self.__convert_to_prepared(', ', data)
            binds = list(data.values())

        self.__connect()

        cursor = self.__get_cursor()
        cursor.execute(sql, binds)
        cursor.close()

        self.memcache_purge()

        return True

    def __get_binds(self, data=tuple()):
        if len(data) == 0:
            return tuple()

        binds = []
        for value in list(data.values()):
            if (value == 'current_timestamp'):
                binds.append(value)
            else:
                binds.append('%s')

        return binds

    def __get_cursor(self):
        return self.__mysql.cursor(prepared=True,
                                   cursor_class=MySQLCursorDict)

    def nth(self, index, sql, binds=tuple()):
        records = self.query(sql, binds)

        if index < len(records):
            return records[index]
        else:
            return None

    def query(self, sql, binds=tuple()):
        results_from_cache = self.memcache_retrieve()
        if results_from_cache is not None:
            return results_from_cache

        self.__connect()

        is_select = False
        if re.match('^\(?select ', sql) or re.match('^show ', sql):
            is_select = True

        cursor = self.__get_cursor()

        try:
            cursor.execute(sql, binds)
        except mysql.connector.errors.ProgrammingError as e:
            raise DataStoreException(
                    'execution of this query:\n\n'
                    + sql
                    + "\n\n"
                    + (repr(binds) if binds is not None else '')
                    + '\n\nproduced this error:\n\n'
                    + e.msg)

        if is_select:
            results = []
            for result in cursor:
                results.append(result)

            if results.count(self) == 1:
                results = results[0]

            self.memcache_store(results)
        else:
            results = True

        cursor.close()

        return results

    def rollback(self):
        '''Rolls back the active transaction.'''
        if self.__mysql is None:
            raise DataStoreException(
                'transaction cannot be rolled back becase a database '
                + 'connection has not been established yet')
        else:
            self.__mysql.rollback()


class DataStoreProvider(metaclass=Singleton):
    '''Defines the main mechanism for retrieving a handle to a configured data
       store.'''

    def get_data_store_handle(self):
        '''Get the active data store handle against which to execute
           operations.'''
        if ConfigManager.value('data store') == 'mysql':
            try:
                self.__dsh
            except AttributeError:
                self.__dsh = DataStoreMySQL()

            return self.__dsh
        else:
            raise DataStoreException(
                'configured data store is not currently supported')

__all__ = ['DataStoreMySQL', 'DataStoreProvider', 'RDBMSBase']
