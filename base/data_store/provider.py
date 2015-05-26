# ----- Info ------------------------------------------------------------------

__author__ = 'Michael Montero <mcmontero@gmail.com>'

# ----- Imports ---------------------------------------------------------------

from .exception import DataStoreException
from .exception import DataStoreDuplicateKeyException
from .exception import DataStoreForeignKeyException
from tinyAPI.base.config import ConfigManager
from tinyAPI.base.data_store.memcache import Memcache

import logging
import os
import pymysql
import random
import re
import threading
import time
import tinyAPI.base.context as Context

__all__ = [
    'assert_is_dsh',
    'auto_tx_start',
    'auto_tx_stop_commit',
    'auto_tx_stop_rollback',
    'DataStoreMySQL',
    'DataStoreProvider',
    'RDBMSBase'
]

# ----- Thread Local Data -----------------------------------------------------

_thread_local_data = threading.local()

# ----- Public Functions ------------------------------------------------------

def assert_is_dsh(dsh):
    if not isinstance(dsh, __DataStoreBase):
        raise DataStoreException(
            'provided value is not instance of __DataStoreBase')


def autonomous_tx_start(connection, db):
    dsh = DataStoreMySQL()
    dsh.set_persistent(False).select_db(connection, db)
    return dsh


def autonomous_tx_stop_commit(dsh, ignore_exceptions=False):
    assert_is_dsh(dsh)
    dsh.commit(ignore_exceptions)
    dsh.close()


def autonomous_tx_stop_rollback(dsh, ignore_exceptions=False):
    assert_is_dsh(dsh)
    dsh.rollback(ignore_exceptions)
    dsh.close()

# ----- Private Classes -------------------------------------------------------

class __DataStoreBase(object):
    '''Defines the base level class from which all data store types (like
       RDBMS) should inherit.'''

    def __init__(self):
        self._connection_name = None
        self._charset = 'utf8'
        self._db_name = None
        self._memcache = None
        self._memcache_key = None
        self._memcache_ttl = None
        self._cached_data = {}
        self._ping_interval = 300
        self._inactive_since = time.time()
        self.requests = 0
        self.hits = 0

        self.persistent = True
        if Context.env_cli() is True:
            self.persistent = False

# ----- Public Classes --------------------------------------------------------

class RDBMSBase(__DataStoreBase):
    '''Defines a data store that handles interactions with a RDBMS (MySQL,
       PostgreSQL, etc.).'''

    def close(self):
        '''Manually close the database connection.'''
        raise NotImplementedError


    def commit(self):
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
        if self._memcache_key is None or Context.env_unit_test():
            return

        if self._memcache is None:
            self._memcache = Memcache()
        self._memcache.purge(self._memcache_key)


    def memcache_retrieve(self):
        '''If the data needs to be cached, cache it.'''
        if self._memcache_key is None or Context.env_unit_test():
            return None

        data = self._cached_data.get(self._memcache_key, None)
        if data is None:
            if self._memcache is None:
                self._memcache = Memcache()

            data = self._memcache.retrieve(self._memcache_key)
            if data is not None:
                self._cached_data[self._memcache_key] = data

        return data


    def memcache_store(self, data):
        '''If there is data and it should be cached, cache it.'''
        if self._memcache_key is None or Context.env_unit_test():
            return

        if self._memcache is None:
            self._memcache = Memcache()
        self._memcache.store(self._memcache_key, data, self._memcache_ttl)


    def nth(self, index, sql, binds=tuple()):
        '''Return the value at the Nth position of the result set.'''
        return None


    def one(self, sql, binds=tuple(), obj=None):
        '''Return the first (and only the first) of the result set.'''
        record = self.nth(0, sql, binds)
        if obj is None:
            return record

        if record is None:
            raise RuntimeError('no data is present to assign to object')

        for key, value in record.items():
            setattr(obj, key, value)


    def query(self, query, binds = []):
        '''Execute an arbitrary query and return all of the results.'''
        return None


    def _reset_memcache(self):
        self._memcache_key = None
        self._memcache_ttl = None


    def rollback(self):
        '''Manually rollback the active transaction.'''
        raise NotImplementedError


    def select_db(self, connection, db):
        '''Select which connection and database schema to use.'''
        if self._connection_name != connection or self._db_name != db:
            self.__mysql = None

        self._connection_name = connection
        self._db_name = db
        return self


    def set_charset(self, charset):
        '''Set the character for the RDBMS.'''
        self._charset = charset
        return self


    def set_persistent(self, persistent):
        self.persistent = persistent
        return self


class DataStoreMySQL(RDBMSBase):
    '''Manages interactions with configured MySQL servers.'''

    def __init__(self):
        super(DataStoreMySQL, self).__init__()

        self.__mysql = None
        self.__cursor = None
        self.__row_count = None


    def close(self):
        '''Close the active database connection.'''
        self.__close_cursor()

        self._inactive_since = time.time()

        if self.__mysql:
            if self.persistent is False:
                self.__mysql.close()
                self.__mysql = None

        if self._memcache is not None:
            if self.persistent is False:
                self._memcache.close()
                self._memcache = None
            self._cached_data = {}


    def __close_cursor(self):
        if self.__cursor is not None:
            self.__cursor.close()
            self.__cursor = None


    def commit(self, ignore_exceptions=False):
        '''Commit the active transaction.'''
        if self.__mysql is None:
            if not ignore_exceptions:
                raise DataStoreException(
                    'transaction cannot be committed because a database '
                    + 'connection has not been established yet')
        else:
            if Context.env_unit_test():
                return
            else:
                self.__mysql.commit()


    def connect(self):
        '''Perform the tasks required for connecting to the database.'''
        if self.persistent is True:
            self.requests += 1

        if self.__mysql:
            if self.persistent is True:
                if time.time() - self._inactive_since >= \
                   self._ping_interval - 3:
                    self.__mysql.ping(True)
                else:
                    self.hits += 1
            return

        if not self._connection_name:
            raise DataStoreException(
                'cannot connect to MySQL because a connection name has not '
                + 'been provided')

        connection_data = ConfigManager().value('mysql connection data')
        if self._connection_name not in connection_data:
                raise DataStoreException(
                    'the MySQL connection name you provided is invalid')

        if not self._db_name:
            raise DataStoreException(
                'cannot connection to MySQL because no database name was '
                + 'selected')

        config = {
            'user': connection_data[self._connection_name][1],
            'passwd': connection_data[self._connection_name][2],
            'host': connection_data[self._connection_name][0],
            'database': self._db_name,
            'charset': self._charset,
            'autocommit': False
        }

        self.__mysql = pymysql.connect(**config)



    def connection_id(self):
        self.connect()
        return self.__mysql.thread_id()


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
        record = self.nth(0, sql, binds)
        if record is None:
            return None

        return list(record.values())[0]


    def create(self, target, data=tuple(), return_insert_id=True):
        if len(data) == 0:
            return None

        keys = list(data.keys())
        binds = self.__get_binds(data)
        vals = self.__get_values(data.values())

        sql  = 'insert into ' + target + '('
        sql += ', '.join(keys)
        sql += ')'
        sql += ' values ('
        sql += ', '.join(binds)
        sql += ')'

        self.connect()

        cursor = self.__get_cursor()

        try:
            cursor.execute(sql, vals)
        except pymysql.err.IntegrityError as e:
            errno, message = e.args

            if errno == 1062:
                raise DataStoreDuplicateKeyException(message)
            elif errno == 1452:
                raise DataStoreForeignKeyException(message)
            else:
                raise
        except pymysql.err.ProgrammingError as e:
            errno, message = e.args

            raise DataStoreException(
                    self.__format_query_execution_error(
                                sql, message, binds))

        self.__row_count = cursor.rowcount

        id = None
        if return_insert_id:
            id = cursor.lastrowid

        self.__close_cursor()

        return id


    def delete(self, target, data=tuple()):
        sql = 'delete from ' + target

        binds = None
        if len(data) > 0:
            sql += ' where ' + self.__convert_to_prepared(', ', data)
            binds = list(data.values())

        self.connect()

        cursor = self.__get_cursor()

        cursor.execute(sql, binds)

        self.__row_count = cursor.rowcount

        self.memcache_purge()

        self.__close_cursor()
        self._reset_memcache()

        return True


    def __format_query_execution_error(self, sql, message, binds=tuple()):
        return ('execution of this query:\n\n'
                + sql
                + "\n\n"
                + (repr(binds) if binds is not None else '')
                + '\n\nproduced this error:\n\n'
                + message)


    def __get_binds(self, data=tuple()):
        if len(data) == 0:
            return tuple()

        binds = []
        for value in list(data.values()):
            if re.match('current_timestamp', str(value)) is not None:
                binds.append(value)
            else:
                binds.append('%s')

        return binds


    def __get_cursor(self):
        if self.__cursor is not None:
            return self.__cursor

        self.__cursor = self.__mysql.cursor(pymysql.cursors.DictCursor)

        return self.__cursor


    def get_row_count(self):
        return self.__row_count


    def __get_values(self, data=tuple()):
        if len(data) == 0:
            return tuple()

        values = []
        for value in data:
            if re.match('current_timestamp', str(value)) is None:
                values.append(value)

        return values


    def nth(self, index, sql, binds=tuple()):
        records = self.query(sql, binds)

        if index < len(records):
            return records[index]
        else:
            return None


    def query(self, sql, binds=tuple()):
        results_from_cache = self.memcache_retrieve()
        if results_from_cache is not None:
            self._reset_memcache()
            return results_from_cache

        self.connect()

        is_select = False
        if re.match('^\(?select ', sql) or re.match('^show ', sql):
            is_select = True

        cursor = self.__get_cursor()

        try:
            cursor.execute(sql, binds)
        except pymysql.err.IntegrityError as e:
            errno, message = e.args

            if errno == 1062:
                raise DataStoreDuplicateKeyException(message)
            elif errno == 1452:
                raise DataStoreForeignKeyException(message)
            else:
                raise
        except pymysql.err.ProgrammingError as e:
            errno, message = e.args

            raise DataStoreException(
                    self.__format_query_execution_error(
                                sql, message, binds))

        self.__row_count = cursor.rowcount

        if is_select:
            results = cursor.fetchall()
            if results == ():
                results = []

            self.memcache_store(results)
        else:
            results = True

        self.__close_cursor()
        self._reset_memcache()

        return results


    def rollback(self, ignore_exceptions=False):
        '''Rolls back the active transaction.'''
        if self.__mysql is None:
            if not ignore_exceptions:
                raise DataStoreException(
                    'transaction cannot be rolled back because a database '
                    + 'connection has not been established yet')
        else:
            self.__mysql.rollback()


class DataStoreProvider(object):
    '''Defines the main mechanism for retrieving a handle to a configured data
       store.'''

    __persistent_connections = {}

    def __init__(self):
        self.pid = os.getpid()


    def get_data_store_handle(self, persistent=False):
        '''Get the active data store handle against which to execute
           operations.'''
        if ConfigManager.value('data store') == 'mysql':
            if not hasattr(_thread_local_data, 'dsh'):
                if persistent is True:
                    if self.pid not in self.__persistent_connections:
                        self.__persistent_connections[self.pid] = \
                            DataStoreMySQL()

                    _thread_local_data.dsh = \
                        self.__persistent_connections[self.pid]
                else:
                    _thread_local_data.dsh = \
                        DataStoreMySQL().set_persistent(False)

            if Context.env_unit_test() is False and random.randint(1, 50) == 1:
                log_file = ConfigManager.value('app log file')
                if log_file is not None:
                    requests = _thread_local_data.dsh.requests
                    hits = _thread_local_data.dsh.hits

                    try:
                        hit_ratio = str((hits / requests) * 100) + '%'
                    except ZeroDivisionError:
                        hit_ratio = 'NA'

                    lines = [
                        '\n----- Persistent Connection Stats (start) ---------'
                        + '-------------------',
                        'PID #' + str(self.pid),
                        'Requests: ' + '{0:,}'.format(requests),
                        'Hits: ' + '{0:,}'.format(hits),
                        'Hit Ratio: ' + hit_ratio,
                        '----- Persistent Connection Stats (stop) ------------'
                        + '-----------------'
                    ]

                    logging.basicConfig(filename = log_file)
                    logging.critical('\n'.join(lines))
                    logging.shutdown()

            return _thread_local_data.dsh
        else:
            raise DataStoreException(
                'configured data store is not currently supported')
