# ----- Info ------------------------------------------------------------------

__author__ = 'Michael Montero <mcmontero@gmail.com>'

# ----- Imports ---------------------------------------------------------------

from .exception import TableBuilderException
from inspect import stack

import re

__all__ = [
    'RefTable',
    'Table'
]

# ----- Private Classes  ------------------------------------------------------

class __MySQLColumn(object):
    '''Defines shared data and functionality for all types of columns.'''

    def __init__(self, name):
        self._name = name
        self._not_null = None
        self._unique = None
        self._default = None
        self._primary_key = False
        self._on_update = None


    def default_value(self, default):
        self._default = default
        return self


    def get_default_term(self):
        if self._default is None:
            if self._not_null is None or self._not_null is False:
                return 'default null'
            else:
                return None

        term = 'default '
        if re.match('current_timestamp', str(self._default)):
            term += self._default
        else:
            term += "'" + str(self._default) + "'"

        return term


    def get_on_update_term(self):
        if self._on_update is None:
            return None
        else:
            return 'on update ' + self._on_update


    def get_name(self):
        return self._name


    def not_null(self):
        self._not_null = True
        return self


    def on_update(self, value):
        self._on_update = value
        return self


    def primary_key(self):
        self._primary_key = True
        return self


    def unique(self):
        self._unique = True
        return self

# ----- Protected Classes  ----------------------------------------------------

class _MySQLNumericColumn(__MySQLColumn):
    '''Defines a numeric MySQL column.'''

    TYPE_BIT = 1
    TYPE_TINYINT = 2
    TYPE_SMALLINT = 3
    TYPE_MEDIUMINT = 4
    TYPE_INT = 5
    TYPE_BIGINT = 6
    TYPE_DECIMAL = 7
    TYPE_FLOAT = 8
    TYPE_DOUBLE = 9
    TYPE_REAL = 10

    def __init__(self, name):
        super(_MySQLNumericColumn, self).__init__(name)

        self.__type_id = None
        self.__max_display_width = None
        self.__precision = None
        self.__scale = None
        self.__unsigned = None
        self.__zero_fill = None
        self.__auto_increment = None


    def auto_increment(self):
        self.__auto_increment = True
        return self


    def decimal_type(self, type_id, precision, scale):
        self.__validate_type_id(type_id)

        self.__type_id = type_id
        self.__precision = precision
        self.__scale = scale

        return self


    def float_type(self, precision):
        self.__type_id = self.TYPE_FLOAT
        self.__precision = precision
        return self


    def get_definition(self):
        terms = [self._name]

        if self.__type_id == self.TYPE_BIT:
            terms.append(self.__with_max_display_width('bit'))
        elif self.__type_id == self.TYPE_TINYINT:
            terms.append(self.__with_max_display_width('tinyint'))
        elif self.__type_id == self.TYPE_SMALLINT:
            terms.append(self.__with_max_display_width('smallint'))
        elif self.__type_id == self.TYPE_MEDIUMINT:
            terms.append(self.__with_max_display_width('mediumint'))
        elif self.__type_id == self.TYPE_INT:
            terms.append(self.__with_max_display_width('int'))
        elif self.__type_id == self.TYPE_BIGINT:
            terms.append(self.__with_max_display_width('bigint'))
        elif self.__type_id == self.TYPE_DECIMAL:
            terms.append(self.__with_precision_and_scale('decimal'))
        elif self.__type_id == self.TYPE_FLOAT:
            terms.append(self.__with_precision('float'))
        elif self.__type_id == self.TYPE_DOUBLE:
            terms.append(self.__with_precision_and_scale('double'))
        elif self.__type_id == self.TYPE_REAL:
            terms.append(self.__with_precision_and_scale('real'))
        else:
            raise TableBuilderException('unrecognized numeric column type "'
                                         + self.__type_id
                                         + '"')

        if self.__unsigned is True:
            terms.append('unsigned')

        if self.__zero_fill is True:
            terms.append('zerofill')

        if self._not_null is True:
            terms.append('not null')

        if self.__auto_increment is True:
            terms.append('auto_increment')

        if self._primary_key is False and self._unique is True:
            terms.append('unique')

        default_term = self.get_default_term()
        if default_term is not None:
            terms.append(default_term)

        if self._primary_key is True:
            terms.append('primary key')

        return ' '.join(terms)


    def integer_type(self, type_id, max_display_width=None):
        self.__validate_type_id(type_id)

        self.__type_id = type_id
        self.__max_display_width = max_display_width

        return self


    def unsigned(self):
        self.__unsigned = True
        return self


    def __validate_type_id(self, type_id):
        if type_id not in [self.TYPE_BIT,
                           self.TYPE_TINYINT,
                           self.TYPE_SMALLINT,
                           self.TYPE_MEDIUMINT,
                           self.TYPE_INT,
                           self.TYPE_BIGINT,
                           self.TYPE_DECIMAL,
                           self.TYPE_FLOAT,
                           self.TYPE_DOUBLE,
                           self.TYPE_REAL]:
            raise TableBuilderException('the type ID provided was invalid')


    def __with_max_display_width(self, type):
        if self.__max_display_width is None:
            return type
        else:
            return type + "(" + str(self.__max_display_width) + ")"


    def __with_precision(self, type):
        if self.__precision is None:
            return type
        else:
            return type + "(" + str(self.__precision) + ")"


    def __with_precision_and_scale(self, type):
        if self.__precision is None or self.__scale is None:
            return type
        else:
            return (type
                    + "("
                    + str(self.__precision)
                    + ", "
                    + str(self.__scale)
                    + ")")


    def zero_fill(self):
        self.__zero_fill = True
        return self


class _MySQLStringColumn(__MySQLColumn):
    '''Defines a string MySQL column.'''

    TYPE_CHAR = 1
    TYPE_VARCHAR = 2
    TYPE_BINARY = 3
    TYPE_VARBINARY = 4
    TYPE_TINYBLOB = 5
    TYPE_BLOB = 6
    TYPE_MEDIUMBLOB = 7
    TYPE_LONGBLOB = 8
    TYPE_TINYTEXT = 9
    TYPE_TEXT = 10
    TYPE_MEDIUMTEXT = 11
    TYPE_LONGTEXT = 12
    TYPE_ENUM = 13
    TYPE_SET = 14

    def __init__(self, name):
        super(_MySQLStringColumn, self).__init__(name)

        self.__type_id = None
        self.__length = None
        self.__charset = 'utf8'
        self.__collation = 'utf8_unicode_ci'
        self.__list = []


    def binary_type(self, type_id, length=None):
        self.__validate_type_id(type_id)

        self.__type_id = type_id
        self.__length = length

        return self


    def blob_type(self, type_id, length=None):
        self.__validate_type_id(type_id)

        if type_id != self.TYPE_BLOB and length is not None:
            raise TableBuilderException(
                'you can only specify the length if the column is blob')

        self.__type_id = type_id
        self.__length = length

        return self


    def char_type(self, type_id, length=None):
        self.__validate_type_id(type_id)

        self.__type_id = type_id
        self.__length = length

        return self


    def charset(self, charset):
        self.__charset = charset
        return self


    def collation(self, name):
        self.__collation = name
        return self


    def __format_list(self):
        list = []
        for value in self.__list:
            list.append("'" + str(value) + "'")

        return ', '.join(list)


    def get_definition(self):
        terms = [self._name]

        if self.__type_id == self.TYPE_CHAR:
            terms.append('char(' + str(self.__length) + ')')
        elif self.__type_id == self.TYPE_VARCHAR:
            terms.append('varchar(' + str(self.__length) + ')')
        elif self.__type_id == self.TYPE_BINARY:
            terms.append('binary(' + str(self.__length) + ')')
        elif self.__type_id == self.TYPE_VARBINARY:
            terms.append('varbinary(' + str(self.__length) + ')')
        elif self.__type_id == self.TYPE_TINYBLOB:
            terms.append('tinyblob')
        elif self.__type_id == self.TYPE_BLOB:
            terms.append('blob(' + str(self.__length) + ')')
        elif self.__type_id == self.TYPE_MEDIUMBLOB:
            terms.append('mediumblob')
        elif self.__type_id == self.TYPE_LONGBLOB:
            terms.append('longblob')
        elif self.__type_id == self.TYPE_TINYTEXT:
            terms.append('tinytext')
        elif self.__type_id == self.TYPE_TEXT:
            terms.append(('text'
                          + ('' if self.__length is None else
                                '(' + str(self.__length) + ')')))
        elif self.__type_id == self.TYPE_MEDIUMTEXT:
            terms.append('mediumtext')
        elif self.__type_id == self.TYPE_LONGTEXT:
            terms.append('longtext')
        elif self.__type_id == self.TYPE_ENUM:
            terms.append('enum(' + self.__format_list() + ')')
        elif self.__type_id == self.TYPE_SET:
            terms.append('set(' + self.__format_list() + ')')
        else:
            raise TableBuilderException('unrecognized string column type "'
                                         + self.__type_id
                                         + '"')

        if self.__type_id not in [self.TYPE_TINYBLOB,
                                  self.TYPE_BLOB,
                                  self.TYPE_MEDIUMBLOB,
                                  self.TYPE_LONGBLOB,
                                  self.TYPE_VARBINARY,
                                  self.TYPE_BINARY]:
            if self.__charset is not None:
                terms.append('character set ' + self.__charset)

            if self.__collation is not None:
                terms.append('collate ' + self.__collation)

        if self._not_null is True:
            terms.append('not null')

        if self._primary_key is False and self._unique is True:
            terms.append('unique')

        default_term = self.get_default_term()
        if default_term is not None:
            terms.append(default_term)

        if self._primary_key is True:
            terms.append('primary key')

        return ' '.join(terms)


    def list_type(self, type_id, values=tuple()):
        self.__validate_type_id(type_id)

        self.__type_id = type_id
        self.__list = values
        return self


    def text_type(self, type_id, length=None):
        self.__validate_type_id(type_id)

        if type_id != self.TYPE_TEXT and length is not None:
            raise TableBuilderException(
                'you can only specify the length if the column is text')

        self.__type_id = type_id
        self.__length = length
        return self


    def __validate_type_id(self, type_id):
        if type_id not in [self.TYPE_CHAR,
                           self.TYPE_VARCHAR,
                           self.TYPE_BINARY,
                           self.TYPE_VARBINARY,
                           self.TYPE_TINYBLOB,
                           self.TYPE_BLOB,
                           self.TYPE_MEDIUMBLOB,
                           self.TYPE_LONGBLOB,
                           self.TYPE_TINYTEXT,
                           self.TYPE_TEXT,
                           self.TYPE_MEDIUMTEXT,
                           self.TYPE_LONGTEXT,
                           self.TYPE_ENUM,
                           self.TYPE_SET]:
            raise TableBuilderException('the type ID provided was invalid')


class _MySQLDateTimeColumn(__MySQLColumn):
    '''Defines a date/time MySQL column.'''

    TYPE_DATE = 1
    TYPE_DATETIME = 2
    TYPE_TIMESTAMP = 3
    TYPE_TIME = 4
    TYPE_YEAR = 5

    def __init__(self, name):
        super(_MySQLDateTimeColumn, self).__init__(name)

        self.__type_id = None
        self.__precision = None


    def date_time_type(self, type_id):
        self.__validate_type_id(type_id)

        self.__type_id = type_id
        return self


    def get_definition(self):
        terms = [self._name]

        precision = ''
        if self.__precision is not None:
            precision = '({})'.format(self.__precision)

        if self.__type_id == self.TYPE_DATE:
            terms.append('date' + precision)
        elif self.__type_id == self.TYPE_DATETIME:
            terms.append('datetime' + precision)
        elif self.__type_id == self.TYPE_TIMESTAMP:
            terms.append('timestamp' + precision)
        elif self.__type_id == self.TYPE_TIME:
            terms.append('time' + precision)
        elif self.__type_id == self.TYPE_YEAR:
            terms.append('year' + precision)
        else:
            raise TableBuilderException(
                'unrecognized date/time column type "{}"'
                    .format(self.__type_id)
            )

        if self._not_null is True:
            terms.append('not null')

        if self._primary_key is False and self._unique is True:
            terms.append('unique')

        default_term = self.get_default_term()
        if default_term is not None:
            terms.append(default_term)

        if self._primary_key is True:
            terms.append('primary key')

        if self._on_update is not None:
            terms.append(self.get_on_update_term())

        return ' '.join(terms)


    def precision(self, precision):
        self.__precision = precision
        return self


    def __validate_type_id(self, type_id):
        if type_id not in [self.TYPE_DATE,
                           self.TYPE_DATETIME,
                           self.TYPE_TIMESTAMP,
                           self.TYPE_TIME,
                           self.TYPE_YEAR]:
            raise TableBuilderException('the type ID provided was invalid')

# ----- Public Classes  -------------------------------------------------------

class Table(object):
    '''Allows for the description of a table that can be compiled to SQL.'''

    def __init__(self, db_name, name):
        self.__active_column = None
        self.__charset = 'utf8'
        self.__collation = 'utf8_unicode_ci'
        self.__columns = []
        self.__db_name = db_name
        self.__dependencies = []
        self.__engine = 'innodb'
        self.__foreign_keys = []
        self.__indexed_cols = {}
        self.__indexes = []
        self.__map = {}
        self.__name = name
        self.__primary_key = []
        self.__rows = []
        self.__temporary = False
        self.__unique_keys = []


    def ai(self):
        '''Makes the active column auto increment.'''
        self.__assert_active_column_is_set(stack()[0][3])

        if not isinstance(self.__active_column, _MySQLNumericColumn):
            raise TableBuilderException(
                'a non-numeric column cannot be set to auto increment')

        self.__active_column.auto_increment()

        return self


    def __add_column(self, column):
        self.__validate_name_does_not_exist_and_register(column.get_name())

        self.__active_column = column
        self.__columns.append(column)


    def __add_indexed_cols(self, cols=tuple()):
        for i in range(len(cols)):
            self.__indexed_cols[','.join(cols[0:i + 1])] = True


    def __assert_active_column_is_set(self, caller):
        if self.__active_column is None:
            raise TableBuilderException(
                'call to "' + caller + '" invalid until column is defined')


    def bin(self, name, length, not_null=False):
        '''Define a binary column.'''
        self.__add_column(
            _MySQLStringColumn(name)
                .binary_type(_MySQLStringColumn.TYPE_BINARY, length))

        self.__set_attributes(not_null, None, None)

        return self


    def bit(self, name, not_null=False, num_bits=None):
        '''Define a column of bits.'''
        self.__add_column(
            _MySQLNumericColumn(name)
                .integer_type(_MySQLNumericColumn.TYPE_BIT, num_bits))

        self.__set_attributes(not_null, None, None)

        return self


    def bint(self,
             name,
             not_null=False,
             max_display_width=None,
             unsigned=False,
             zero_fill=False):
        '''Define a bit integer column.'''
        self.__add_column(
            _MySQLNumericColumn(name)
                .integer_type(_MySQLNumericColumn.TYPE_BIGINT,
                              max_display_width))

        self.__set_attributes(not_null, unsigned, zero_fill)

        return self


    def blob(self, name, length, not_null=False):
        '''Define a binary large object.'''
        self.__add_column(
            _MySQLStringColumn(name)
                .blob_type(_MySQLStringColumn.TYPE_BLOB, length))

        self.__set_attributes(not_null, None, None)

        return self


    def bool(self, name, not_null=False):
        '''Define a boolean column.'''
        self.tint(name, not_null, 1)
        return self


    def char(self, name, length, not_null=False):
        '''Define a character column.'''
        self.__add_column(
            _MySQLStringColumn(name)
                .char_type(_MySQLStringColumn.TYPE_CHAR, length))

        self.__set_attributes(not_null, None, None)

        return self


    def coll(self, name):
        '''Set the collation on the active column.'''
        if not isinstance(self.__active_column, _MySQLStringColumn):
            raise TableBuilderException(
                'collation can only be set on string columns')

        self.__active_column.collation(name)
        return self


    def created(self, precision=None):
        '''Create a standardized date_created column.'''
        self.dtt('date_created', True, precision)
        return self


    def dec(self,
            name,
            not_null=False,
            precision=None,
            scale=None,
            unsigned=False,
            zero_fill=False):
        '''Define a decimal column.'''
        self.__add_column(
            _MySQLNumericColumn(name)
                .decimal_type(_MySQLNumericColumn.TYPE_DECIMAL,
                              precision,
                              scale))

        self.__set_attributes(not_null, unsigned, zero_fill)

        return self


    def defv(self, default):
        '''Set the default value for the active column.'''
        self.__assert_active_column_is_set(stack()[0][3])

        self.__active_column.default_value(default)
        return self


    def double(self,
               name,
               not_null=False,
               precision=None,
               scale=None,
               unsigned=False,
               zero_fill=False):
        '''Define a double column.'''
        self.dec(name, not_null, precision, scale, unsigned, zero_fill)
        return self


    def dt(self, name, not_null=False):
        '''Define a date column.'''
        self.__add_column(
            _MySQLDateTimeColumn(name)
                .date_time_type(_MySQLDateTimeColumn.TYPE_DATE))

        self.__set_attributes(not_null, None, None)

        return self


    def dtt(self, name, not_null=False, precision=None):
        '''Define a date/time column.'''
        self.__add_column(
            _MySQLDateTimeColumn(name)
                .date_time_type(_MySQLDateTimeColumn.TYPE_DATETIME)
                .precision(precision)
        )

        self.__set_attributes(not_null, None, None)

        return self


    def email(self, name, not_null=False):
        '''Define a column to store an email address.'''
        if name != 'email_address' and not re.match('em_', name):
            raise TableBuilderException(
                    'email column must be named "email_address" or start with '
                    + '"em_"')

        self.vchar(name, 100, not_null)

        return self


    def engine(self, name):
        '''Set the engine for the table.'''
        engine = name.lower()
        if engine not in ['innodb', 'myisam']:
            raise TableBuilderException(
                'the engine "' + engine + '" is invalid')

        self.__engine = engine
        return self


    def enum(self, name, list=tuple(), not_null=False):
        '''Define an enumeration.'''
        self.__add_column(
            _MySQLStringColumn(name)
                .list_type(_MySQLStringColumn.TYPE_ENUM, list))

        self.__set_attributes(not_null, None, None)

        return self


    def fk(self,
           parent_table,
           on_delete_cascade=True,
           cols=tuple(),
           parent_cols=tuple()):
        '''Define a foreign key constraint.'''
        if len(cols) == 0:
            self.__assert_active_column_is_set(stack()[0][3])
            cols = [self.__active_column.get_name()]

        for col in cols:
            if col not in self.__map:
                raise TableBuilderException(
                    ('column "' + col + '" cannot be used in foreign key '
                     + 'because it has not been defined'))

        if len(parent_cols) == 0:
            parent_cols = ['id']

        self.__foreign_keys.append([parent_table,
                                    on_delete_cascade,
                                    cols,
                                    parent_cols])

        self.__dependencies.append(parent_table.split('_')[0])

        return self


    def fixed(self,
              name,
              not_null=False,
              precision=None,
              scale=None,
              unsigned=False,
              zero_fill=False):
        '''Define a fixed decimal column.'''
        self.dec(name, not_null, precision, scale, unsigned, zero_fill)
        return self


    def float(self,
              name,
              not_null=False,
              precision=None,
              unsigned=False,
              zero_fill=False):
        '''Define a float column.'''
        self.__add_column(
            _MySQLNumericColumn(name)
                .float_type(precision))

        self.__set_attributes(not_null, unsigned, zero_fill)

        return self


    def money(self, name, not_null=False):
        '''Define a column suitable for storing monetary values.'''
        self.float(name, not_null, 53)
        return self


    def get_db_name(self):
        '''Return the database name for this table.'''
        return self.__db_name


    def get_definition(self):
        '''Return the SQL necessary to create this table.'''
        if len(self.__columns) == 0:
            raise TableBuilderException(
                'the table cannot be defined because it has no columns')

        terms = []
        for col in self.__columns:
            terms.append('    ' + col.get_definition())

        if len(self.__unique_keys) > 0:
            for i in range(0, len(self.__unique_keys)):
                terms.append('    unique key '
                             + self.__name
                             + '_' + str(i)
                             + '_uk ('
                             + ', '.join(self.__unique_keys[i])
                             + ')')

        if len(self.__primary_key) > 0:
            terms.append('    primary key '
                         + self.__name
                         + '_pk ('
                         + ', '.join(self.__primary_key)
                         + ')')

        table_config = []
        if self.__engine is not None:
            table_config.append('engine = ' + self.__engine)

        if self.__charset is not None:
            table_config.append('default charset = ' + self.__charset)

        if self.__collation is not None:
            table_config.append('collate = ' + self.__collation)

        table_config = ' '.join(table_config)

        return ('create'
                + ('' if self.__temporary is False else ' temporary')
                + ' table '
                + self.__name
                + '\n(\n'
                + ',\n'.join(terms)
                + '\n)'
                + ('' if len(table_config) == 0 else ' ' + table_config)
                + ';')


    def get_dependencies(self):
        '''Return a list of this tables dependencies.'''
        return self.__dependencies


    def get_foreign_key_definitions(self):
        '''Get SQL statements to create foreign keys defined for this table.'''
        if len(self.__foreign_keys) == 0:
            return []

        fks = []
        for i in range(0, len(self.__foreign_keys)):
            parent_table = self.__foreign_keys[i][0]
            on_delete_cascade = self.__foreign_keys[i][1]
            cols = self.__foreign_keys[i][2]
            parent_cols = self.__foreign_keys[i][3]

            constraint_name = self.__name + '_' + str(i) + '_fk'

            fks.append(('   alter table ' + self.__name + "\n"
                        + 'add constraint '
                        + self.__name
                        + '_' + str(i)
                        + '_fk\n'
                        + '   foreign key ('
                        + ', '.join(cols)
                        + ')\n    references ' + parent_table
                        + ('' if len(parent_cols) == 0 else
                            ' (' + ', '.join(parent_cols) + ')')
                        + ('' if on_delete_cascade is False else
                            '\n     on delete cascade')))

        return fks


    def get_index_definitions(self):
        '''Get SQL statements to create indexes defined for this table.'''
        indexes = []
        for i in range(0, len(self.__indexes)):
            indexes.append(('create index '
                            + self.__name
                            + '_' + str(i)
                            + '_idx\n          on '
                            + self.__name
                            + '\n             ('
                            + ', '.join(self.__indexes[i])
                            + ')'))

        return indexes


    def get_insert_statements(self):
        '''Get SQL statements to add data that should be inserted into this
           table.'''
        if len(self.__rows) == 0:
            return None

        rows = []
        for row in self.__rows:
            statement = 'insert into ' + self.__name + "\n(\n"

            cols = []
            for col in self.__columns:
                cols.append('    ' + col.get_name())

            statement += (',\n'.join(cols)
                          + "\n)\nvalues\n(\n")

            vals = []
            for val in row:
                if val == 'current_timestamp':
                    vals.append('    current_timestamp')
                elif re.match('current_date', str(val)):
                    vals.append(val)
                elif val is None:
                    vals.append('    null')
                else:
                    vals.append("    '" + str(val) + "'")

            statement += ',\n'.join(vals) + '\n);\ncommit;'
            rows.append(statement)

        return rows


    def get_unindexed_foreign_keys(self):
        '''Return a list of foreign keys that do not have indexes.'''
        unindexed = []
        for fk in self.__foreign_keys:
            parent_table = fk[0]
            on_delete_cascade = fk[1]
            cols = fk[2]
            parent_cols = fk[3]

            if ','.join(cols) not in self.__indexed_cols.keys():
                unindexed.append([self.__name, parent_table, cols, parent_cols])

        return unindexed


    def id(self, name, unique=False, serial=False):
        '''Define a standard ID column.'''
        if name != 'id' and not re.search('_id$', name):
            raise TableBuilderException(
                'an ID column must be named "id" or end in "_id"')

        self.__add_column(
            _MySQLNumericColumn(name)
                .integer_type(_MySQLNumericColumn.TYPE_BIGINT)
                .unsigned()
                .not_null())

        if unique is True:
            self.__active_column.unique()

        if serial is True:
            self.__active_column.auto_increment()

        return self


    def idx(self, cols=tuple()):
        '''Define an index.'''
        if len(cols) == 0:
            self.__assert_active_column_is_set(stack()[0][3])
            cols = [self.__active_column.get_name()]

        for col in cols:
            composite = col.split(' ')
            if composite[0] not in self.__map:
                raise TableBuilderException(
                    'column "' + col + '" cannot be used in index because '
                     + 'it has not been defined')

            if len(composite) == 2:
                if composite[1] != 'asc' and composite[1] != 'desc':
                    raise TableBuilderException(
                        'columns can only be modified using "asc" or "desc"')

        self.__indexes.append(cols)
        self.__add_indexed_cols(cols)

        return self


    def ins(self, *args):
        '''Insert a new row into this table when it is created.'''
        if len(args) != len(self.__columns):
            raise TableBuilderException(
                'this table has ' + str(len(self.__columns)) + ' column(s) but '
                + 'your insert data only has ' + str(len(args)))

        self.__rows.append(args)
        return self


    def int(self,
            name,
            not_null=False,
            max_display_width=None,
            unsigned=False,
            zero_fill=False):
        '''Define an integer column.'''
        self.__add_column(
            _MySQLNumericColumn(name)
                .integer_type(_MySQLNumericColumn.TYPE_INT, max_display_width))

        self.__set_attributes(not_null, unsigned, zero_fill)

        return self


    def lat(self, name, not_null=False):
        '''Define a latitude column.'''
        if name != 'latitude' and not re.match('^lat_', name):
            raise TableBuilderException(
                    'latitude column must be named "latitude" or start with '
                    + '"lat_"')

        self.float(name, not_null, 53)

        return self


    def lblob(self, name, not_null=False):
        '''Define a long binary large object column.'''
        self.__add_column(
            _MySQLStringColumn(name)
                .blob_type(_MySQLStringColumn.TYPE_LONGBLOB))

        self.__set_attributes(not_null, None, None)

        return self


    def long(self, name, not_null=False):
        '''Define a longitude column.'''
        if name != 'longitude' and not re.match('^long_', name):
            raise TableBuilderException(
                    'longitude column must be named "longitude" or start with '
                    + '"long_"')

        self.float(name, not_null, 53)

        return self


    def ltext(self, name, not_null=False):
        '''Define a long text column.'''
        self.__add_column(
            _MySQLStringColumn(name)
                .text_type(_MySQLStringColumn.TYPE_LONGTEXT))

        self.__set_attributes(not_null, None, None)

        return self


    def mblob(self, name, not_null=False):
        '''Define a medium binary large object column.'''
        self.__add_column(
            _MySQLStringColumn(name)
                .blob_type(_MySQLStringColumn.TYPE_MEDIUMBLOB))

        self.__set_attributes(not_null, None, None)

        return self


    def mint(self,
             name,
             not_null=False,
             max_display_width=None,
             unsigned=False,
             zero_fill=False):
        '''Define a medium integer column.'''
        self.__add_column(
            _MySQLNumericColumn(name)
                .integer_type(_MySQLNumericColumn.TYPE_MEDIUMINT,
                              max_display_width))

        self.__set_attributes(not_null, None, None)

        return self


    def mtext(self, name, not_null=False):
        '''Define a medium text column.'''
        self.__add_column(
            _MySQLStringColumn(name)
                .text_type(_MySQLStringColumn.TYPE_MEDIUMTEXT))

        self.__set_attributes(not_null, None, None)

        return self


    def pk(self, cols=tuple()):
        '''Define the table's primary key.'''
        if len(cols) == 0:
            self.__assert_active_column_is_set(stack()[0][3])
            self.__active_column.primary_key()
            self.__add_indexed_cols([self.__active_column.get_name()])
        else:
            for col in cols:
                if col not in self.__map:
                    raise TableBuilderException(
                        'column "' + col + '" cannot be used in primary key '
                        + 'because it has not been defined')

                self.__primary_key.append(col)

        self.__add_indexed_cols(self.__primary_key)

        return self


    def serial(self, name='id'):
        '''Define a standard MySQL serial column.'''
        self.id(name, False, True).pk()
        return self


    def set(self, name, list=tuple(), not_null=False):
        '''Define a set column.'''
        self.__add_column(
            _MySQLStringColumn(name)
                .list_type(_MySQLStringColumn.TYPE_SET, list))

        self.__set_attributes(not_null, None, None)

        return self


    def __set_attributes(self, not_null, unsigned, zero_fill):
        if not_null is True:
            self.__active_column.not_null()

        if unsigned is True:
            self.__active_column.unsigned()

        if zero_fill is True:
            self.__active_column.zero_fill()


    def sint(self,
             name,
             not_null=False,
             max_display_width=None,
             unsigned=False,
             zero_fill=False):
        '''Define a small integer column.'''
        self.__add_column(
            _MySQLNumericColumn(name)
                .integer_type(_MySQLNumericColumn.TYPE_SMALLINT,
                              max_display_width))

        self.__set_attributes(not_null, unsigned, zero_fill)

        return self


    def tblob(self, name, not_null=False):
        '''Define a tiny binary large object.'''
        self.__add_column(
            _MySQLStringColumn(name)
                .blob_type(_MySQLStringColumn.TYPE_TINYBLOB))

        self.__set_attributes(not_null, None, None)

        return self


    def temp(self):
        '''Define the table as temporary.'''
        self.__temporary = True
        return self


    def text(self, name, not_null=False, length=None):
        '''Define a text column.'''
        self.__add_column(
            _MySQLStringColumn(name)
                .text_type(_MySQLStringColumn.TYPE_TEXT, length))

        self.__set_attributes(not_null, None, None)

        return self


    def ti(self, name, not_null=False):
        '''Define a time column.'''
        self.__add_column(
            _MySQLDateTimeColumn(name)
                .date_time_type(_MySQLDateTimeColumn.TYPE_TIME))

        self.__set_attributes(not_null, None, None)

        return self


    def tint(self,
             name,
             not_null=False,
             max_display_width=None,
             unsigned=False,
             zero_fill=False):
        '''Define a tiny integer column.'''
        self.__add_column(
            _MySQLNumericColumn(name)
                .integer_type(_MySQLNumericColumn.TYPE_TINYINT,
                              max_display_width))

        self.__set_attributes(not_null, unsigned, zero_fill)

        return self


    def ts(self, name, not_null=False, precision=None):
        '''Define a timestamp column.'''
        self.__add_column(
            _MySQLDateTimeColumn(name)
                .date_time_type(_MySQLDateTimeColumn.TYPE_TIMESTAMP)
                .precision(precision)
        )

        self.__set_attributes(not_null, None, None)

        return self


    def ttext(self, name, not_null=False):
        '''Define a tiny text column.'''
        self.__add_column(
            _MySQLStringColumn(name)
                .text_type(_MySQLStringColumn.TYPE_TINYTEXT))

        self.__set_attributes(not_null, None, None)

        return self


    def uk(self, cols=tuple()):
        '''Define a unique key.'''
        if len(cols) == 0:
            self.__assert_active_column_is_set(stack()[0][3])
            self.__active_column.unique()
            self.__add_indexed_cols([self.__active_column.get_name()])
        else:
            unique_key = []
            for col in cols:
                if col not in self.__map:
                    raise TableBuilderException(
                        'column "' + col + '" cannot be used in unique key '
                        + 'because it has not been defined')

                unique_key.append(col)

            self.__unique_keys.append(unique_key)
            self.__add_indexed_cols(unique_key)

        return self


    def updated(self, precision=None):
        '''Create a standardized date_updated column.'''
        self.ts('date_updated', False, precision)

        if precision is None:
            self.__active_column.default_value(
                '2000-01-01 00:00:00'
            )
            self.__active_column.on_update(
                'current_timestamp'
            )
        else:
            self.__active_column.default_value(
                'current_timestamp({})'.format(precision)
            )
            self.__active_column.on_update(
                'current_timestamp({})'.format(precision)
            )

        return self


    def __validate_name_does_not_exist_and_register(self, name):
        if name in self.__map:
            raise TableBuilderException(
                'the column "' + name + '" already exists')

        self.__map.update({name: True})


    def vbin(self, name, length, not_null=False):
        '''Define a variable length binary column.'''
        self.__add_column(
            _MySQLStringColumn(name)
                .char_type(_MySQLStringColumn.TYPE_VARBINARY, length))

        self.__set_attributes(not_null, None, None)

        return self


    def vchar(self, name, length, not_null=False):
        '''Define a variable length character column.'''
        self.__add_column(
            _MySQLStringColumn(name)
                .char_type(_MySQLStringColumn.TYPE_VARCHAR, length))

        self.__set_attributes(not_null, None, None)

        return self


    def yr(self, name, not_null=False, precision=4):
        '''Define a year column.'''
        self.__add_column(
            _MySQLDateTimeColumn(name)
                .date_time_type(_MySQLDateTimeColumn.TYPE_YEAR)
                .precision(precision)
        )

        self.__set_attributes(not_null, None, None)

        return self


class RefTable(Table):
    '''Create a reference table that maps ID values to strings.'''

    def __init__(self, db_name, name):
        self.__validate_name(name)

        super(RefTable, self).__init__(db_name, name)

        self.__ids = {}
        self.__display_orders = {}
        self.__display_order = 1

        self.serial() \
            .vchar('value', 100, True) \
            .int('display_order')


    def add(self, id, value, display_order=None):
        '''Add a new ID to value mapping to the table.'''
        if id in self.__ids:
            raise TableBuilderException(
                'the ID "' + str(id) + '" is already defined')

        if display_order in self.__display_orders:
            raise TableBuilderException(
                'the display order "' + str(display_order) + '" is already '
                + 'defined')

        if display_order is None:
            display_order = self.__display_order
            self.__display_order += 1

        self.ins(id, re.sub("'", "''", value), display_order)

        self.__ids[id] = True
        self.__display_orders[display_order] = True

        return self


    def __validate_name(self, name):
        if not re.match('^\w+_ref_', name):
            raise TableBuilderException(
                'the name of the reference table must contain "_ref_"')


class View(object):
    '''Implements a view of a table.'''

    def __init__(self, db_name, name):
        self.db_name = db_name
        self.name = name
        self.base_table_name = None


    def get_db_name(self):
        return self.db_name


    def get_definition(self):
        if self.base_table_name is None:
            raise TableBuilderException(
                'a base table was not configured for the view "'
                + self.name
                + '"')

        return ('create view ' + self.name + '\n'
                + '         as select *\n'
                + '              from ' + self.base_table_name)


    def tbl(self, name):
        self.base_table_name = name
        return self
