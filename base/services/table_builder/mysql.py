'''mysql.py -- Implementation of the Table Builder for MySQL.'''

__author__ = 'Michael Montero <mcmontero@gmail.com>'

# ----- Import ---------------------------------------------------------------

from .exception import TableBuilderException
from inspect import stack

# ----- Private Classes  -----------------------------------------------------

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

    def get_default_term(self):
        if self._default is None:
            if self._not_null is None or self._not_null is False:
                return 'default null'
            else:
                return None

        term = 'default '
        if self._default == 'current_timestamp':
            term += 'current_timestamp'
        else:
            term += "'" + self._default + "'"

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

    def primary_key(self):
        self._primary_key = True

    def unique(self):
        self._unique = True


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
        self.__type_id = TYPE_FLOAT
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
            raise TableBuilderException('the type ID provided is invalid')

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

# ----- Public Classes  ------------------------------------------------------

class Table(object):
    '''Allows for the description of a table that can be compiled to SQL.'''

    def __init__(self, db_name, name):
        self.__db_name = db_name
        self.__name = name
        self.__engine = 'innodb'
        self.__columns = []
        self.__map = {}
        self.__active_column = None
        self.__temporary = False
        self.__primary_key = []
        self.__unique_keys = []
        self.__foreign_keys = []
        self.__dependencies = []
        self.__indexes = []
        self.__rows = []
        self.__indexed_cols = []
        self.__charset = 'utf8'
        self.__collation = 'utf8_unicode_ci'

    def ai():
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
        for col in cols:
            self.__indexed_cols.append({','.join(cols[0:]): True})

    def __assert_active_column_is_set(self, caller):
        if self.__active_column is None:
            raise TableBuilderException(
                'call to "' + caller + '" invalid until column is defined')

    def bin(self, name, length, not_null=False):
        '''Define a binary column.'''
        self.__add_column(
            _MySQLNumericColumn(name)
                .binary_type(_MySQLNumericColumn.TYPE_BINARY, length))

        self.__set_attributes(not_null, None, None)

        return self

    def bit(self, not_null=False, num_bits=None):
        '''Define a column of bits.'''
        self.__add_column(
            _MySQLNumericColumn(name)
                .integer_type(_MySQLNumericColumn.TYPE_BIT, num_bits))

        self.__set_attributes(not_null, None, None)

        return self

    def bint(self,
             name,
             not_null=False,
             unsigned=False,
             max_display_width=None,
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
        self.tint(name, 1, not_null)
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

    def created(self):
        '''Create a standardized date_created column.'''
        self.dtt('date_created', true)
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

    def dtt(self, name, not_null=False):
        '''Define a date/time column.'''
        self.__add_column(
            _MySQLDateTimeColumn(name)
                .date_type_type(_MySQLDateTimeColumn.TYPE_DATETIME))

        self.__set_attributes(not_null, None, None)

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
            MySQLStringColumn(name)
                .list_type(MySQLStringColumn.TYPE_ENUM, list))

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
        self.__dependencies.append(parent_table)

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
              not_null=False,
              precision=None,
              unsigned=False,
              zero_fill=False):
        '''Define a float column.'''
        self.__add_column(
            MySQLNumericColumn(name)
                .float_type(precision))

        self.__set_attributes(not_null, unsigned, zero_fill)

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
                terms.append('    unique key'
                             + self._name
                             + '_' + i
                             + '_uk ('
                             + ', '.join(self.__unique_keys[i])
                             + ')')

        if len(self.__primary_key) > 0:
            terms.append('    primary key'
                         + self._name
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
                + ('' if len(table_config) == 0 else ' ' + table_config))

    def get_dependencies(self):
        '''Return a list of this tables dependencies.'''
        return self.__dependencies

    def id(self, name, unique=False, serial=False):
        '''Define a standard ID column.'''
        if name != 'id' and not re.match('_id$', name):
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
            cols.append(self.__active_column.get_name())

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

    def int(self,
            name,
            not_null=False,
            unsigned=False,
            max_display_width=None,
            zero_fill=False):
        '''Define an integer column.'''
        self.__add_column(
            _MySQLNumericColumn(name)
                .integer_type(_MySQLNumericColumn.TYPE_INT, max_display_width))

        self.__set_attributes(not_null, unsigned, zero_fill)

        return self

    def lblob(self, name, not_null=False):
        '''Define a long binary large object column.'''
        self.__add_column(
            MySQLStringColumn(name)
                .blob_type(MySQLStringColumn.TYPE_LONGBLOB))

        self.__set_attributes(not_null, None, None)

        return self

    def ltext(self, name, not_null=False):
        '''Define a long text column.'''
        self.__add_column(
            MySQLStringColumn(name)
                .text_type(MySQLStringColumn.TYPE_LONGTEXT))

        self.__set_attributes(not_null, None, None)

        return self

    def mblob(self, name, not_null=False):
        '''Define a medium binary large object column.'''
        self.__add_column(
            MySQLStringColumn(name)
                .blob_type(MySQLStringColumn.TYPE_MEDIUMBLOB))

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
            MySQLNumericColumn(name)
                .integer_type(MySQLNumericColumn.TYPE_MEDIUMINT,
                              max_display_width))

        self.__set_attributes(not_null, None, None)

        return self

    def mtext(self, name, not_null=False):
        '''Define a medium text column.'''
        self.__add_column(
            MySQLStringColumn(name)
                .text_type(MySQLStringColumn.TYPE_MEDIUMTEXT))

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
            MySQLStringColumn(name)
                .list_type(MySQLStringColumn.TYPE_SET, list))

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
            MySQLNumericColumn(name)
                .integer_type(MySQLNumericColumn.TYPE_SMALLINT,
                              max_display_width))

        self.__set_attributes(not_null, unsigned, zero_fill)

        return self

    def tblob(self, name, not_null=False):
        '''Define a tiny binary large object.'''
        self.__add_column(
            MySQLStringColumn(name)
                .blob_type(MySQLStringColumn.TYPE_TINYBLOB))

        self.__set_attribute(not_null, None, None)

        return self

    def temp(self):
        '''Define the table as temporary.'''
        self.__temporary = True
        return self

    def text(self, name, not_null=False, length=None):
        '''Define a text column.'''
        self.__add_column(
            MySQLStringColumn(name)
                .text_type(MySQLStringColumn.TYPE_TEXT, length))

        self.__set_attributes(not_null, None, None)

        return self

    def ti(self, name, not_null=False):
        '''Define a time column.'''
        self.__add_column(
            MySQLDateTimeColumn(name)
                .date_time_type(MySQLDateTimeColumn.TYPE_TIME))

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
            MySQLNumericColumn(name)
                .integer_type(MySQLNumericColumn.TYPE_TINYINT,
                              max_display_width))

        self.__set_attributes(not_null, unsigned, zero_fill)

        return self

    def ts(self, name, not_null=False):
        '''Define a timestamp column.'''
        self.__add_column(
            MySQLDateTimeColumn(name)
                .date_time_type(MySQLDateTimeColumn.TYPE_TIMESTAMP))

        self.__set_attribute(not_null, None, None)

        return self

    def ttext(self, name, not_null=False):
        '''Define a tiny text column.'''
        self.__add_column(
            MySQLStringColumn(name)
                .text_type(MySQLStringColumn.TYPE_TINYTEXT))

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

    def updated(self):
        '''Create a standardized date_updated column.'''
        self.ts('date_updated', true)
        self.__active_column.on_update('current_timestamp')
        return self

    def __validate_name_does_not_exist_and_register(self, name):
        if name in self.__map:
            raise TableBuilderException(
                'the column"' + name + '" already exists')

        self.__map.update({name: True})

    def vbin(self, length, not_null=False):
        '''Define a variable length binary column.'''
        self.__add_column(
            MySQLStringColumn(name)
                .char_type(MySQLStringColumn.TYPE_VARBINARY, length))

        self.__set_attributes(not_null, None, None)

        return self

    def vchar(self, name, length, not_null=False):
        '''Define a variable length character column.'''
        self.__add_column(
            MySQLStringColumn(name)
                .char_type(MySQLStringColumn.TYPE_VARCHAR, length))

        self.__set_attributes(not_null, None, None)

        return self

    def yr(name, not_null=False, num_digits=4):
        '''Define a year column.'''
        self.__add_column(MySQLDateTimeColumn(name).year(num_digits))
        self.__set_attributes(not_null, None, None)
        return self

__all__ = ['Table']
