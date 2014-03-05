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

    def decimal_type(self, type_id, precision, scale):
        self.__validate_type_id(type_id)

        self.__type_id = type_id
        self.__precision = precision
        self.__scale = scale

    def float_type(self, precision):
        self.__type_id = TYPE_FLOAT
        self.__precision = precision

    def get_definition(self):
        terms = []

        if self.__type_id == TYPE_BIT:
            terms.append(self.__with_max_display_width('bit'))
        elif self.__type_id == TYPE_TINYINT:
            terms.append(self.__with_max_display_width('tinyint'))
        elif self.__type_id == TYPE_SMALLINT:
            terms.append(self.__with_max_display_width('smallint'))
        elif self.__type_id == TYPE_MEDIUMINT:
            terms.append(self.__with_max_display_width('mediumint'))
        elif self.__type_id == TYPE_INT:
            terms.append(self.__with_max_display_width('int'))
        elif self.__type_id == TYPE_BIGINT:
            terms.append(self.__width_max_display_width('bigint'))
        elif self.__type_id == TYPE_DECIMAL:
            terms.append(self.__with_precision_and_scale('decimal'))
        elif self.__type_id == TYPE_FLOAT:
            terms.append(self.__with_precision('float'))
        elif self.__type_id == TYPE_DOUBLE:
            terms.append(self.__with_precision_and_scale('double'))
        elif self.__type_id == TYPE_REAL:
            terms.append(self.__with_precision_and_scale('real'))
        else:
            raise TableBuilderException(('unrecognized numeric column type "'
                                         + self.__type_id
                                         + '"'))

        if self.__unsigned is True:
            terms.append('unsigned')

        if self.__zero_fill is True:
            terms.append('zerofill')

        if self.__not_null is True:
            terms.append('not null')

        if self.__auto_increment is True:
            terms.append('auto_increment')

        if self.__primary_key is False and self.__unique is True:
            terms.append('unique')

        default_term = self.__get_default_term()
        if default_term is not None:
            terms.append(default_term)

        if self.__primary_key is True:
            terms.append('primary key')

        return ' '.join(terms)

    def integer_type(self, type_id, max_display_width=None):
        self.__validate_type_id(type_id)

        self.__type_id = type_id
        self.__max_display_width = max_display_width

    def unsigned(self):
        self.__unsigned = True

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
        self.__primary_keys = []
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

    def __assert_active_column_is_set(self, caller):
        if not isinstance(self.__active_column, __MySQLColumn):
            raise TableBuilderException(
                'call to "' + caller + '" invalid until column is defined')

    def int(self,
            name,
            not_null=False,
            unsigned=False,
            max_display_width=None,
            zero_fill = False):
        '''Define an integer column.'''
        column = _MySQLNumericColumn(name)
        column.integer_type(_MySQLNumericColumn.TYPE_INT, max_display_width)

        self.__add_column(column)

        self.__set_attributes(not_null, unsigned, zero_fill)

        return self

    def __set_attributes(self, not_null, unsigned, zero_fill):
        if not_null is True:
            self.__active_column.not_null()

        if unsigned is True:
            self.__active_column.unsigned()

        if zero_fill is True:
            self.__active_column.zero_fill()

    def __validate_name_does_not_exist_and_register(self, name):
        print(self.__map)
        if name in self.__map:
            raise TableBuilderException(
                'the column"' + name + '" already exists')

        self.__map.update({name: True})

__all__ = ['Table']
