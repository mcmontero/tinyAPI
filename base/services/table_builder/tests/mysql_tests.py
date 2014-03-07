'''mysql.py -- Unit tests for MySQL Table Builder.'''

__author__ = 'Michael Montero <mcmontero@gmail.com>'

# ----- Import ---------------------------------------------------------------

from tinyAPI.base.services.table_builder.exception \
    import TableBuilderException
from tinyAPI.base.services.table_builder.mysql \
    import _MySQLDateTimeColumn, \
           _MySQLNumericColumn, \
           _MySQLStringColumn
import tinyAPI
import unittest

# ----- Tests ----------------------------------------------------------------

class TableBuilderMySQLTestCase(unittest.TestCase):

    def test_add_column_dupe_exceptions(self):
        try:
            tinyAPI.Table('db', 'abc').bit('def').bint('def')

            self.fail('Was able to add two columns with the same name.');
        except TableBuilderException as e:
            self.assertEqual('the column "def" already exists',
                             e.get_message())

    def test_numeric_column_bit(self):
        self.assertEqual(
            "abcdef bit unsigned zerofill not null "
            + "auto_increment unique default \'1\'",
            _MySQLNumericColumn('abcdef')
                .integer_type(_MySQLNumericColumn.TYPE_BIT)
                .default_value(1)
                .auto_increment()
                .not_null()
                .unique()
                .unsigned()
                .zero_fill()
                .get_definition())

    def test_numeric_column_bint(self):
        self.assertEqual(
            "abcdef bigint(13) unsigned zerofill not null "
            + "auto_increment unique default \'1\'",
            _MySQLNumericColumn('abcdef')
                .integer_type(_MySQLNumericColumn.TYPE_BIGINT, 13)
                .default_value(1)
                .auto_increment()
                .not_null()
                .unique()
                .unsigned()
                .zero_fill()
                .get_definition())

    def test_numeric_column_mint(self):
        self.assertEqual(
            "abcdef mediumint(13) unsigned zerofill not null "
            + "auto_increment unique default \'1\'",
            _MySQLNumericColumn('abcdef')
                .integer_type(_MySQLNumericColumn.TYPE_MEDIUMINT, 13)
                .default_value(1)
                .auto_increment()
                .not_null()
                .unique()
                .unsigned()
                .zero_fill()
                .get_definition())

    def test_numeric_column_int(self):
        self.assertEqual(
            "abcdef int(13) unsigned zerofill not null "
            + "auto_increment unique default \'1\'",
            _MySQLNumericColumn('abcdef')
                .integer_type(_MySQLNumericColumn.TYPE_INT, 13)
                .default_value(1)
                .auto_increment()
                .not_null()
                .unique()
                .unsigned()
                .zero_fill()
                .get_definition())

    def test_numeric_column_sint(self):
        self.assertEqual(
            "abcdef smallint(13) unsigned zerofill not null "
            + "auto_increment unique default \'1\'",
            _MySQLNumericColumn('abcdef')
                .integer_type(_MySQLNumericColumn.TYPE_SMALLINT, 13)
                .default_value(1)
                .auto_increment()
                .not_null()
                .unique()
                .unsigned()
                .zero_fill()
                .get_definition())

    def test_numeric_column_tint(self):
        self.assertEqual(
            "abcdef tinyint(13) unsigned zerofill not null "
            + "auto_increment unique default \'1\'",
            _MySQLNumericColumn('abcdef')
                .integer_type(_MySQLNumericColumn.TYPE_TINYINT, 13)
                .default_value(1)
                .auto_increment()
                .not_null()
                .unique()
                .unsigned()
                .zero_fill()
                .get_definition())

    def test_numeric_column_dec(self):
        self.assertEqual(
            "abcdef decimal(12, 34) unsigned zerofill not null "
            + "auto_increment unique default \'1\'",
            _MySQLNumericColumn('abcdef')
                .decimal_type(_MySQLNumericColumn.TYPE_DECIMAL, 12, 34)
                .default_value(1)
                .auto_increment()
                .not_null()
                .unique()
                .unsigned()
                .zero_fill()
                .get_definition())

    def test_numeric_column_float(self):
        self.assertEqual(
            "abcdef float(12) unsigned zerofill not null "
            + "auto_increment unique default \'1.0\'",
            _MySQLNumericColumn('abcdef')
                .float_type(12)
                .default_value(1.0)
                .auto_increment()
                .not_null()
                .unique()
                .unsigned()
                .zero_fill()
                .get_definition())

    def test_table_engine_exceptions(self):
        try:
            tinyAPI.Table('db', 'abc').engine('def')

            self.fail('Was able to set the engine to an invalid value.')
        except TableBuilderException as e:
            self.assertEqual('the engine "def" is invalid', e.get_message())

    def test_table_get_definition_exceptions(self):
        try:
            tinyAPI.Table('db', 'abc').get_definition()

            self.fail('Was able to get table definition even though no '
                      + 'columns were provided.')
        except TableBuilderException as e:
            self.assertEqual(
                'the table cannot be defined because it has no columns',
                e.get_message())

    def test_table_simple(self):
        text = '''create table abc
(
    id bigint unsigned not null auto_increment unique
) engine = innodb default charset = utf8 collate = utf8_unicode_ci;'''

        self.assertEqual(text,
                         tinyAPI.Table('db', 'abc')
                            .engine('InnoDB')
                            .id('id', True, True)
                            .get_definition())

    def test_table_multi_numeric_columns(self):
        text = '''create table abc
(
    id bigint unsigned not null auto_increment unique,
    def tinyint(1) default null,
    ghi float(12) default null
) engine = myisam default charset = utf8 collate = utf8_unicode_ci;'''

        self.assertEqual(text,
                         tinyAPI.Table('db', 'abc')
                            .engine('myisam')
                            .id('id', True, True)
                            .bool('def')
                            .float('ghi', False, 12)
                            .get_definition())

    def test_table_calling_set_attribute(self):
        text = '''create table abc
(
    def int default null,
    ghi int unsigned zerofill default null
) engine = innodb default charset = utf8 collate = utf8_unicode_ci;'''

        self.assertEqual(text,
                         tinyAPI.Table('db', 'abc')
                            .int('def')
                            .int('ghi', False, None, True, True)
                            .get_definition())

    def test_table_helper_attribute_methods(self):
        text = '''create table abc
(
    def int default null,
    ghi int unique default null,
    jkl int auto_increment default null,
    mno int default '123'
) engine = innodb default charset = utf8 collate = utf8_unicode_ci;'''

        self.assertEqual(text,
                         tinyAPI.Table('db', 'abc')
                            .int('def')
                            .int('ghi')
                                .uk()
                            .int('jkl')
                                .ai()
                            .int('mno')
                                .defv(123)
                            .get_definition())

    def test_table_active_column_is_primary_key(self):
        text = '''create table abc
(
    def int default null primary key
) engine = innodb default charset = utf8 collate = utf8_unicode_ci;'''

        self.assertEqual(text,
                         tinyAPI.Table('db', 'abc')
                            .int('def')
                                .pk()
                            .get_definition())

    def test_temporary_table(self):
        text = '''create temporary table abc
(
    id bigint unsigned not null auto_increment unique
) engine = innodb default charset = utf8 collate = utf8_unicode_ci;'''

        self.assertEqual(text,
                         tinyAPI.Table('db', 'abc')
                            .temp()
                            .id('id', True, True)
                            .get_definition())

    def test_table_composite_primary_key_exceptions(self):
        try:
            tinyAPI.Table('db', 'abc') \
                .int('def') \
                .pk(['def', 'ghi']) \
                .get_definition()

            self.fail('Was able to get the definition for a table even '
                      + 'though one of the columns in the primary key did not '
                      + 'exist.')
        except TableBuilderException as e:
            self.assertEqual(
                'column "ghi" cannot be used in primary key because it has not '
                + 'been defined', e.get_message())

    def test_table_composite_primary_key(self):
        text = '''create table abc
(
    def int default null,
    ghi int default null,
    primary key abc_pk (def, ghi)
) engine = innodb default charset = utf8 collate = utf8_unicode_ci;'''

        self.assertEqual(text,
                         tinyAPI.Table('db', 'abc')
                            .int('def')
                            .int('ghi')
                            .pk(['def', 'ghi'])
                            .get_definition())

    def test_table_composite_unique_key_exceptions(self):
        try:
            tinyAPI.Table('db', 'abc') \
                .int('def') \
                .uk(['def', 'ghi']) \
                .get_definition()

            self.fail('Was able to get the definition for a table even '
                      + 'though one of the columns in a unique key did not '
                      + 'exist.')
        except TableBuilderException as e:
            self.assertEqual(
                'column "ghi" cannot be used in unique key because it has not '
                + 'been defined', e.get_message())

    def test_table_one_composite_unique_key(self):
        text = '''create table abc
(
    def int default null,
    ghi int default null,
    jkl int default null,
    unique key abc_0_uk (def, ghi)
) engine = innodb default charset = utf8 collate = utf8_unicode_ci;'''

        self.assertEqual(text,
                         tinyAPI.Table('db', 'abc')
                            .int('def')
                            .int('ghi')
                            .int('jkl')
                            .uk(['def', 'ghi'])
                            .get_definition())

    def test_table_multiple_composite_unique_keys(self):
        text = '''create table abc
(
    def int default null,
    ghi int default null,
    jkl int default null,
    unique key abc_0_uk (def, ghi),
    unique key abc_1_uk (ghi, jkl)
) engine = innodb default charset = utf8 collate = utf8_unicode_ci;'''

        self.assertEqual(text,
                         tinyAPI.Table('db', 'abc')
                            .int('def')
                            .int('ghi')
                            .int('jkl')
                            .uk(['def', 'ghi'])
                            .uk(['ghi', 'jkl'])
                            .get_definition())

    def test_date_time_column_type_exception(self):
        try:
            _MySQLDateTimeColumn('abc').date_time_type(-1)

            self.fail('Was able to set a date time type even though the type '
                      + 'ID provided was invalid.')
        except TableBuilderException as e:
            self.assertEqual('the type ID provided was invalid',
                             e.get_message())

    def test_date_time_column_date(self):
        self.assertEqual(
            "abcdef date not null unique default \'1\'",
            _MySQLDateTimeColumn('abcdef')
                .date_time_type(_MySQLDateTimeColumn.TYPE_DATE)
                .default_value(1)
                .not_null()
                .unique()
                .get_definition())

    def test_date_time_column_datetime(self):
        self.assertEqual(
            "abcdef datetime not null unique default \'1\'",
            _MySQLDateTimeColumn('abcdef')
                .date_time_type(_MySQLDateTimeColumn.TYPE_DATETIME)
                .default_value(1)
                .not_null()
                .unique()
                .get_definition())

    def test_date_time_column_timestamp(self):
        self.assertEqual(
            "abcdef timestamp not null unique default \'1\'",
            _MySQLDateTimeColumn('abcdef')
                .date_time_type(_MySQLDateTimeColumn.TYPE_TIMESTAMP)
                .default_value(1)
                .not_null()
                .unique()
                .get_definition())

    def test_date_time_column_time(self):
        self.assertEqual(
            "abcdef time not null unique default \'1\'",
            _MySQLDateTimeColumn('abcdef')
                .date_time_type(_MySQLDateTimeColumn.TYPE_TIME)
                .default_value(1)
                .not_null()
                .unique()
                .get_definition())

    def test_date_time_column_year_2(self):
        self.assertEqual(
            "abcdef year(2) not null unique default \'1\'",
            _MySQLDateTimeColumn('abcdef')
                .year(2)
                .default_value(1)
                .not_null()
                .unique()
                .get_definition())

    def test_date_time_column_year_4(self):
        self.assertEqual(
            "abcdef year(4) not null unique default \'1\'",
            _MySQLDateTimeColumn('abcdef')
                .year(4)
                .default_value(1)
                .not_null()
                .unique()
                .get_definition())

    def test_table_date_columns_year_2(self):
        text = '''create table abc
(
    def date not null,
    ghi datetime not null,
    jkl timestamp not null,
    mno time not null,
    pqr year(2) not null
) engine = innodb default charset = utf8 collate = utf8_unicode_ci;'''

        self.assertEqual(text,
                         tinyAPI.Table('db', 'abc')
                            .dt('def', True)
                            .dtt('ghi', True)
                            .ts('jkl', True)
                            .ti('mno', True)
                            .yr('pqr', True, 2)
                            .get_definition())

    def test_table_date_columns_year_4(self):
        text = '''create table abc
(
    def date not null,
    ghi datetime not null,
    jkl timestamp not null,
    mno time not null,
    pqr year(4) not null
) engine = innodb default charset = utf8 collate = utf8_unicode_ci;'''

        self.assertEqual(text,
                         tinyAPI.Table('db', 'abc')
                            .dt('def', True)
                            .dtt('ghi', True)
                            .ts('jkl', True)
                            .ti('mno', True)
                            .yr('pqr', True, 4)
                            .get_definition())

    def test_table_created(self):
        text = '''create table abc
(
    id bigint unsigned not null auto_increment unique,
    date_created datetime not null
) engine = innodb default charset = utf8 collate = utf8_unicode_ci;'''

        self.assertEqual(text,
                         tinyAPI.Table('db', 'abc')
                            .id('id', True, True)
                            .created()
                            .get_definition())

    def test_table_updated(self):
        text = '''create table abc
(
    id bigint unsigned not null auto_increment unique,
    date_updated timestamp not null on update current_timestamp
) engine = innodb default charset = utf8 collate = utf8_unicode_ci;'''

        self.assertEqual(text,
                         tinyAPI.Table('db', 'abc')
                            .id('id', True, True)
                            .updated()
                            .get_definition())

    def test_string_validate_type_id_exceptions(self):
        try:
            _MySQLStringColumn('abc').binary_type(-1)

            self.fail('Was able to set binary type even though the ID provided '
                      + 'was invalid.')
        except TableBuilderException as e:
            self.assertEqual('the type ID provided was invalid',
                             e.get_message())

        try:
            _MySQLStringColumn('abc').blob_type(-1)

            self.fail('Was able to set blob type even though the ID provided '
                      + 'was invalid.')
        except TableBuilderException as e:
            self.assertEqual('the type ID provided was invalid',
                             e.get_message())

        try:
            _MySQLStringColumn('abc').char_type(-1)

            self.fail('Was able to set char type even though the ID provided '
                      + 'was invalid.')
        except TableBuilderException as e:
            self.assertEqual('the type ID provided was invalid',
                             e.get_message())

        try:
            _MySQLStringColumn('abc').list_type(-1)

            self.fail('Was able to set list type even though the ID provided '
                      + 'was invalid.')
        except TableBuilderException as e:
            self.assertEqual('the type ID provided was invalid',
                             e.get_message())

        try:
            _MySQLStringColumn('abc').text_type(-1)

            self.fail('Was able to set text type even though the ID provided '
                      + 'was invalid.')
        except TableBuilderException as e:
            self.assertEqual('the type ID provided was invalid',
                             e.get_message())

    def test_string_blob_type_exceptions(self):
        for type_id in [_MySQLStringColumn.TYPE_TINYBLOB,
                        _MySQLStringColumn.TYPE_MEDIUMBLOB,
                        _MySQLStringColumn.TYPE_LONGBLOB]:
            try:
                _MySQLStringColumn('abc').blob_type(type_id, 15)

                self.fail('Was able to specify length even though it is not '
                          + 'allowed for a non-blob column.')
            except TableBuilderException as e:
                self.assertEqual(
                    'you can only specify the length if the column is blob',
                    e.get_message())

    def test_string_text_type_exceptions(self):
        for type_id in [_MySQLStringColumn.TYPE_TINYTEXT,
                        _MySQLStringColumn.TYPE_MEDIUMTEXT,
                        _MySQLStringColumn.TYPE_LONGTEXT]:
            try:
                _MySQLStringColumn('abc').text_type(type_id, 15)

                self.fail('Was able to specify length even though it is not '
                          + 'allowed for a non-text column.')
            except TableBuilderException as e:
                self.assertEqual(
                    'you can only specify the length if the column is text',
                    e.get_message())

    def test_string_binary_binary(self):
        self.assertEqual(
            "abc binary(15) character set def collate ghi default null",
            _MySQLStringColumn('abc')
                .binary_type(_MySQLStringColumn.TYPE_BINARY, 15)
                .charset('def')
                .collation('ghi')
                .get_definition())

    def test_string_binary_varbinary(self):
        self.assertEqual(
            "abc varbinary(15) character set def collate ghi default null",
            _MySQLStringColumn('abc')
                .binary_type(_MySQLStringColumn.TYPE_VARBINARY, 15)
                .charset('def')
                .collation('ghi')
                .get_definition())

    def test_string_blob_tinyblob(self):
        self.assertEqual(
            "abc tinyblob character set def collate ghi default null",
            _MySQLStringColumn('abc')
                .binary_type(_MySQLStringColumn.TYPE_TINYBLOB)
                .charset('def')
                .collation('ghi')
                .get_definition())

    def test_string_blob_blob(self):
        self.assertEqual(
            "abc blob(15) character set def collate ghi default null",
            _MySQLStringColumn('abc')
                .binary_type(_MySQLStringColumn.TYPE_BLOB, 15)
                .charset('def')
                .collation('ghi')
                .get_definition())

    def test_string_blob_mediumblob(self):
        self.assertEqual(
            "abc mediumblob character set def collate ghi default null",
            _MySQLStringColumn('abc')
                .binary_type(_MySQLStringColumn.TYPE_MEDIUMBLOB)
                .charset('def')
                .collation('ghi')
                .get_definition())

    def test_string_blob_longblob(self):
        self.assertEqual(
            "abc longblob character set def collate ghi default null",
            _MySQLStringColumn('abc')
                .binary_type(_MySQLStringColumn.TYPE_LONGBLOB)
                .charset('def')
                .collation('ghi')
                .get_definition())

    def test_string_char_char(self):
        self.assertEqual(
            "abc char(15) character set def collate ghi default null",
            _MySQLStringColumn('abc')
                .char_type(_MySQLStringColumn.TYPE_CHAR, 15)
                .charset('def')
                .collation('ghi')
                .get_definition())

    def test_string_char_varchar(self):
        self.assertEqual(
            "abc varchar(15) character set def collate ghi default null",
            _MySQLStringColumn('abc')
                .char_type(_MySQLStringColumn.TYPE_VARCHAR, 15)
                .charset('def')
                .collation('ghi')
                .get_definition())

    def test_string_list_enum(self):
        self.assertEqual(
            "abc enum('x', 'y') character set def collate ghi default null",
            _MySQLStringColumn('abc')
                .list_type(_MySQLStringColumn.TYPE_ENUM, ['x', 'y'])
                .charset('def')
                .collation('ghi')
                .get_definition())

    def test_string_list_set(self):
        self.assertEqual(
            "abc set('x', 'y') character set def collate ghi default null",
            _MySQLStringColumn('abc')
                .list_type(_MySQLStringColumn.TYPE_SET, ['x', 'y'])
                .charset('def')
                .collation('ghi')
                .get_definition())

    def test_string_types_in_table(self):
        text = '''create table abc
(
    def char(15) character set utf8 collate utf8_unicode_ci not null,
    ghi varchar(16) character set utf8 collate utf8_unicode_ci not null,
    jkl binary(17) character set utf8 collate utf8_unicode_ci not null,
    mno varbinary(18) character set utf8 collate utf8_unicode_ci not null,
    pqr tinyblob character set utf8 collate utf8_unicode_ci not null,
    stu blob(19) character set utf8 collate utf8_unicode_ci not null,
    vwx mediumblob character set utf8 collate utf8_unicode_ci not null,
    yza longblob character set utf8 collate utf8_unicode_ci not null,
    bcd tinytext character set utf8 collate utf8_unicode_ci not null,
    efg text(20) character set utf8 collate utf8_unicode_ci not null,
    hij mediumtext character set utf8 collate utf8_unicode_ci not null,
    klm longtext character set utf8 collate utf8_unicode_ci not null,
    nop enum('a', 'b') character set utf8 collate utf8_unicode_ci not null,
    qrs set('c', 'd') character set utf8 collate utf8_unicode_ci not null
) engine = innodb default charset = utf8 collate = utf8_unicode_ci;'''

        self.assertEqual(text,
                         tinyAPI.Table('db', 'abc')
                            .char('def', 15, True)
                            .vchar('ghi', 16, True)
                            .bin('jkl', 17, True)
                            .vbin('mno', 18, True)
                            .tblob('pqr', True)
                            .blob('stu', 19, True)
                            .mblob('vwx', True)
                            .lblob('yza', True)
                            .ttext('bcd', True)
                            .text('efg', True, 20)
                            .mtext('hij', True)
                            .ltext('klm', True)
                            .enum('nop', ['a', 'b'], True)
                            .set('qrs', ['c', 'd'], True)
                            .get_definition())

    def test_ref_table_exceptions(self):
        try:
            tinyAPI.RefTable('db', 'abc');

            self.fail('Was able to create a reference table even though the '
                      + 'table name was non-standard.')
        except TableBuilderException as e:
            self.assertEqual(
                'the name of the reference table must contain "_ref_"',
                e.get_message())

        try:
            tinyAPI.RefTable('db', 'abc_ref_def').add(1, 'a').add(1, 'b')

            self.fail('Was able to create a reference table even though a '
                      + 'duplicate ID value was used.')
        except TableBuilderException as e:
            self.assertEqual('the ID "1" is already defined', e.get_message())

        try:
            tinyAPI.RefTable('db', 'abc_ref_def').add(1, 'a', 1).add(2, 'b', 1)

            self.fail('Was able to create a reference table even though a '
                      + 'duplicate display order was used.')
        except TableBuilderException as e:
            self.assertEqual('the display order "1" is already defined',
                             e.get_message())

    def test_ref_table(self):
        table_definition = '''create table abc_ref_def
(
    id bigint unsigned not null auto_increment unique,
    value varchar(100) character set utf8 collate utf8_unicode_ci not null,
    display_order int default null
) engine = innodb default charset = utf8 collate = utf8_unicode_ci;'''

        insert_statements = '''insert into abc_ref_def
(
    id,
    value,
    display_order
)
values
(
    '1',
    'one',
    '1'
);
insert into abc_ref_def
(
    id,
    value,
    display_order
)
values
(
    '2',
    'two',
    '2'
);
insert into abc_ref_def
(
    id,
    value,
    display_order
)
values
(
    '3',
    'three',
    '3'
);
'''

        ref_table = tinyAPI.RefTable('db', 'abc_ref_def') \
                        .add(1, 'one', 1) \
                        .add(2, 'two', 2) \
                        .add(3, 'three', 3)

        self.assertEqual(table_definition, ref_table.get_definition())

        actual = ''
        for insert_statement in ref_table.get_insert_statements():
            actual += insert_statement + "\n"

        self.assertEqual(insert_statements, actual)

    def test_table_ai_active_column_is_set_exceptions(self):
        try:
            tinyAPI.Table('db', 'abc').ai()

            self.fail('Was able to set a column as auto-increment even though '
                      + 'no column was defined.')
        except TableBuilderException as e:
            self.assertEqual(
                'call to "ai" invalid until column is defined',
                e.get_message())

    def test_table_defv_active_column_is_set_exceptions(self):
        try:
            tinyAPI.Table('db', 'abc').defv(1)

            self.fail('Was able to set the default value for a olumn even '
                      + 'though no column was defined.')
        except TableBuilderException as e:
            self.assertEqual(
                'call to "defv" invalid until column is defined',
                e.get_message())

    def test_table_pk_active_column_is_set_exceptions(self):
        try:
            tinyAPI.Table('db', 'abc').pk()

            self.fail('Was able to set a column as primary key even though no '
                      + 'column was defined.')
        except TableBuilderException as e:
            self.assertEqual(
                'call to "pk" invalid until column is defined',
                e.get_message())

    def test_table_uk_active_column_is_set_exceptions(self):
        try:
            tinyAPI.Table('db', 'abc').uk()

            self.fail('Was able to set a column as a unique key even though no '
                      + 'column was defined.')
        except TableBuilderException as e:
            self.assertEqual(
                'call to "uk" invalid until column is defined',
                e.get_message())

    def test_table_fk_active_column_is_set_exceptions(self):
        try:
            tinyAPI.Table('db', 'abc').fk('def')

            self.fail('Was able to set a column as a foreign key even though '
                      + 'no column was defined.')
        except TableBuilderException as e:
            self.assertEqual(
                'call to "fk" invalid until column is defined',
                e.get_message())

    def test_table_idx_active_column_is_set_exceptions(self):
        try:
            tinyAPI.Table('db', 'abc').idx()

            self.fail('Was able to set a column as an index even though no '
                      + 'column was defined.')
        except TableBuilderException as e:
            self.assertEqual(
                'call to "idx" invalid until column is defined',
                e.get_message())

    def test_table_foreign_key_and_dependencies_active_column(self):
        text = '''create table abc
(
    id bigint unsigned not null auto_increment unique
) engine = innodb default charset = utf8 collate = utf8_unicode_ci;'''

        table = tinyAPI.Table('db', 'abc') \
                    .id('id', True, True) \
                    .fk('def')

        self.assertEqual(text, table.get_definition())

        text = '''   alter table abc
add constraint abc_0_fk
   foreign key (id)
    references def (id)
     on delete cascade'''

        fks = table.get_foreign_key_definitions()
        self.assertEqual(1, len(fks))
        self.assertEqual(text, fks[0])

        deps = table.get_dependencies()
        self.assertEqual(1, len(deps))
        self.assertTrue('def' in deps)

    def test_foreign_key_full_definition(self):
        text = '''   alter table abc
add constraint abc_0_fk
   foreign key (col_a, col_b)
    references def (col_c, col_d)'''

        fks = tinyAPI.Table('db', 'abc') \
                .int('col_a') \
                .int('col_b') \
                .fk('def', False, ['col_a', 'col_b'], ['col_c', 'col_d']) \
                .get_foreign_key_definitions()

        self.assertEqual(1, len(fks))
        self.assertEqual(text, fks[0])

    def test_table_foreign_key_exceptions(self):
        try:
            tinyAPI.Table('db', 'abc').fk('def', True, ['ghi'])

            self.fail('Was able to create a foreign key even though the column '
                      + 'provided did not exist.')
        except TableBuilderException as e:
            self.assertEqual(
                'column "ghi" cannot be used in foreign key because it has '
                + 'not been defined', e.get_message())

    def test_table_index_exceptions(self):
        try:
            tinyAPI.Table('db', 'abc').idx(['def'])

            self.fail('Was able to create an index even though the column '
                      + 'provided did not exist.')
        except TableBuilderException as e:
            self.assertEqual(
                'column "def" cannot be used in index because it has not been '
                + 'defined', e.get_message())

        try:
            tinyAPI.Table('db', 'abc').int('col_a').idx(['col_a x'])

            self.fail('Was able to create an indexed with an invalid column '
                      + 'modifier for asc/desc.');
        except TableBuilderException as e:
            self.assertEqual(
                'columns can only be modified using "asc" or "desc"',
                e.get_message())

    def test_table_getting_index_definitions(self):
        table = tinyAPI.Table('db', 'abc') \
                    .int('col_a') \
                    .int('col_b') \
                        .idx() \
                    .idx(['col_a asc', 'col_b desc'])
        indexes = table.get_index_definitions()

        self.assertEqual(2, len(indexes))
        self.assertEqual(
            "create index abc_0_idx\n          on abc\n             (col_b)",
            indexes[0])
        self.assertEqual(
            "create index abc_1_idx\n          on abc\n"
            + "             (col_a asc, col_b desc)",
            indexes[1])

    def test_text_type_with_no_length(self):
        self.assertEqual(
            'abc text character set utf8 collate utf8_unicode_ci default null',
            _MySQLStringColumn('abc')
                .text_type(_MySQLStringColumn.TYPE_TEXT)
                .get_definition())

    def test_getting_db_name_from_table(self):
        self.assertEqual('db',
                         tinyAPI.Table('db', 'abc_ref_def').get_db_name())

    def test_getting_db_name_from_ref_table(self):
        self.assertEqual('db',
                         tinyAPI.RefTable('db', 'abc_ref_def').get_db_name())

# ----- Main -----------------------------------------------------------------

if __name__ == '__main__':
    unittest.main()
