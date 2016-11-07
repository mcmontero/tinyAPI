# ----- Info ------------------------------------------------------------------

__author__ = 'Michael Montero <mcmontero@gmail.com>'

# ----- Imports ---------------------------------------------------------------

from .exception import DataStoreException
from .exception import DataStoreDuplicateKeyException
from .exception import DataStoreForeignKeyException
from .Randomizer import Randomizer
from .RDBMSBase import RDBMSBase
from tinyAPI.base.data_store.memcache import Memcache

import psycopg2
import psycopg2.extras
import re
import time
import tinyAPI.base.context as Context

# ----- Public Classes --------------------------------------------------------

class PostgreSQL(RDBMSBase):
    '''
    Manages interactions with configured PostgreSQL servers.
    '''

    def __init__(self):
        super(PostgreSQL, self).__init__()

        self.__postgresql = None
        self.__cursor = None
        self.__row_count = None
        self.__last_row_id = None

    def close(self):
        self.__close_cursor()
        Memcache().clear_local_cache()

        if self.__postgresql:
            if self.persistent is False:
                self.__postgresql.close()
                self.__postgresql = None

        if self._memcache is not None:
            if self.persistent is False:
                self._memcache.close()
                self._memcache = None

    def __close_cursor(self):
        if self.__cursor is not None:
            self.__cursor.close()
            self.__cursor = None

    def commit(self, ignore_exceptions=False):
        if self.__postgresql is None:
            if not ignore_exceptions:
                raise DataStoreException(
                    'transaction cannot be committed because a database '
                    + 'connection has not been established yet'
                )
        else:
            if Context.env_unit_test():
                return
            else:
                self.connect()
                self.__postgresql.commit()

    def connect(self):
        if self.__postgresql:
            if self.should_ping() is True:
                self.query('select 1')
                self.commit()
            return

        if self._settings is None or self._db is None or self._group is None:
            raise DataStoreException(
                'cannot connect to PostgreSQL because data store '
                + 'has not been configured'
            )

        if self._settings[self._group]['durability'] == 'randomizer':
            durability = Randomizer(self._settings[self._group]['hosts'])
        else:
            raise DataStoreException(
                'unrecognized durability algorithm "{}"'
                    .format(self._settings[self._group]['durability'])
            )

        while True:
            host, user, password = durability.next()

            config = {
                'user': user,
                'password': password,
                'host': host,
                'database': self._db
            }

            try:
                self.__postgresql = psycopg2.connect(**config)
                break
            except psycopg2.OperationalError as e:
                durability.next()

        self._inactive_since = time.time()

    def connection_id(self):
        self.connect()
        return self.__postgresql.thread_id()

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
        except psycopg2.IntegrityError as e:
            if e.pgcode == '23505':
                raise DataStoreDuplicateKeyException(e.pgerror)
            elif e.pgcode == '23503':
                raise DataStoreForeignKeyException(e.pgerror)
            else:
                raise
        except psycopg2.ProgrammingError as e:
            raise \
                DataStoreException(
                    self.__format_query_execution_error(
                        sql, e.pgerror, binds
                    )
                )

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
            str_value = str(value)

            if re.match('current_timestamp', str_value) is not None or \
               str_value == 'current_date':
                binds.append(value)
            else:
                binds.append('%s')

        return binds

    def __get_cursor(self):
        if self.__cursor is not None:
            return self.__cursor

        self.__cursor = \
            self.__postgresql.cursor(
                cursor_factory=psycopg2.extras.RealDictCursor
            )

        return self.__cursor

    def get_last_row_id(self):
        return self.__last_row_id

    def get_row_count(self):
        return self.__row_count

    def __get_values(self, data=tuple()):
        if len(data) == 0:
            return tuple()

        values = []
        for value in data:
            str_value = str(value)

            if re.match('current_timestamp', str_value) is None and \
               str_value != 'current_date':
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
        except psycopg2.IntegrityError as e:
            if e.pgcode == '23505':
                raise DataStoreDuplicateKeyException(e.pgerror)
            elif e.pgcode == '23503':
                raise DataStoreForeignKeyException(e.pgerror)
            else:
                raise
        except psycopg2.ProgrammingError as e:
            raise \
                DataStoreException(
                    self.__format_query_execution_error(
                        sql, e.pgerror, binds
                    )
                )

        self.__row_count = cursor.rowcount
        self.__last_row_id = cursor.lastrowid

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
        if self.__postgresql is None:
            if not ignore_exceptions:
                raise DataStoreException(
                    'transaction cannot be rolled back because a database '
                    + 'connection has not been established yet'
                )
        else:
            self.connect()
            self.__postgresql.rollback()
