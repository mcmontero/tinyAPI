# ----- Info ------------------------------------------------------------------

__author__ = 'Michael Montero <mcmontero@gmail.com>'

# ----- Imports ---------------------------------------------------------------

from tinyAPI.base.config import ConfigManager
from tinyAPI.base.data_store.exception import DataStoreException

import datetime
import tinyAPI
import tinyAPI.base.data_store.provider as provider
import unittest

# ----- Tests -----------------------------------------------------------------

class ProviderMySQLTestCase(unittest.TestCase):

    def setUp(self):
        self.__execute_tests = False
        if ConfigManager().value('data store') == 'mysql':
            self.__execute_tests = True

            tinyAPI.dsh.select_db(
                ConfigManager().value('default unit test connection'),
                'tinyAPI'
            )

            tinyAPI.dsh().query(
                '''create table if not exists unit_test_table
                   (
                        id integer not null auto_increment primary key,
                        value integer not null,
                        ti time null,
                        message blob null
                   )''')


    def tearDown(self):
        if self.__execute_tests is True:
            tinyAPI.dsh().query('drop table unit_test_table')


    def test_adding_records_to_table(self):
        if self.__execute_tests is True:
            for i in range(0, 5):
                tinyAPI.dsh().create(
                    'unit_test_table',
                    {'value': i},
                    True)

            for i in range(0, 5):
                self.assertEqual(
                    1,
                    tinyAPI.dsh().count(
                        '''select count(*)
                             from unit_test_table
                            where value = %s''',
                        [i]))


    def test_getting_nth_record_from_table(self):
        if self.__execute_tests is True:
            for i in range(0, 5):
                tinyAPI.dsh().create(
                    'unit_test_table',
                    {'value': i},
                    True)

            results = tinyAPI.dsh().nth(3, 'select value from unit_test_table')
            self.assertEqual(3, results['value'])


    def test_deleting_from_table(self):
        if self.__execute_tests is True:
            for i in range(0, 5):
                tinyAPI.dsh().create(
                    'unit_test_table',
                    {'value': i},
                    True)

            self.assertEqual(
                5,
                tinyAPI.dsh().count('select count(*) from unit_test_table'))

            tinyAPI.dsh().delete('unit_test_table', {'value': 3})

            self.assertEqual(
                4,
                tinyAPI.dsh().count('select count(*) from unit_test_table'))


    def test_asserting_is_dsh_errors(self):
        try:
            provider.assert_is_dsh('abc')

            self.fail('Was able to assert is DSH even though the value '
                      + 'provided was not instance of __DataStoreBase')
        except DataStoreException as e:
            self.assertEqual(
                'provided value is not instance of __DataStoreBase',
                e.get_message())


    def test_two_active_data_store_handles(self):
        dsh_1 = provider.DataStoreMySQL()
        dsh_2 = provider.DataStoreMySQL()

        dsh_1.select_db(
            ConfigManager().value('default unit test connection'),
            'tinyAPI'
        )
        dsh_2.select_db(
            ConfigManager().value('default unit test connection'),
            'tinyAPI'
        )

        self.assertIsInstance(dsh_1.connection_id(), int)
        self.assertIsInstance(dsh_2.connection_id(), int)
        self.assertNotEqual(dsh_1.connection_id(), dsh_2.connection_id())

        self.assertEqual(123, dsh_1.count('select 123 from dual'))
        self.assertEqual(456, dsh_2.count('select 456 from dual'))

        dsh_1.close()
        dsh_2.close()


    def test_use_of_autonomous_transactions(self):
        dsh_1 = \
            provider.autonomous_tx_start(
                ConfigManager().value('default unit test connection'),
                'tinyAPI'
            )
        dsh_2 = \
            provider.autonomous_tx_start(
                ConfigManager().value('default unit test connection'),
                'tinyAPI'
            )

        self.assertIsInstance(dsh_1.connection_id(), int)
        self.assertIsInstance(dsh_2.connection_id(), int)
        self.assertNotEqual(dsh_1.connection_id(), dsh_2.connection_id())

        dsh_1.query(
            '''insert into unit_test_table(
                  id,
                  value)
               values(
                  1000,
                  123)''')
        dsh_2.query(
            '''insert into unit_test_table(
                  id,
                  value)
               values(
                  2000,
                  456)''')

        self.assertEqual(
            1,
            dsh_1.count(
                '''select count(*)
                     from unit_test_table
                    where id = 1000'''))
        self.assertEqual(
            0,
            dsh_1.count(
                '''select count(*)
                     from unit_test_table
                    where id = 2000'''))

        self.assertEqual(
            1,
            dsh_2.count(
                '''select count(*)
                     from unit_test_table
                    where id = 2000'''))
        self.assertEqual(
            0,
            dsh_2.count(
                '''select count(*)
                     from unit_test_table
                    where id = 1000'''))

        provider.autonomous_tx_stop_commit(dsh_1)
        provider.autonomous_tx_stop_rollback(dsh_2)


    def test_row_count(self):
        tinyAPI.dsh().query(
            '''insert into unit_test_table(
                  id,
                  value)
               values(
                  1000,
                  123)''')
        self.assertEqual(1, tinyAPI.dsh().get_row_count())

        tinyAPI.dsh().query(
            '''update unit_test_table
                  set value = 456
                where id = 1''')
        self.assertEqual(0, tinyAPI.dsh().get_row_count())

        tinyAPI.dsh().query(
            '''update unit_test_table
                  set value = 456
                where id = 1000''')
        self.assertEqual(1, tinyAPI.dsh().get_row_count())

        tinyAPI.dsh().delete('unit_test_table', {'id': 1000})
        self.assertEqual(1, tinyAPI.dsh().get_row_count())


    def test_last_row_id_with_select(self):
        tinyAPI.dsh().query(
            '''select 1
                 from dual''')
        self.assertIsNone(tinyAPI.dsh().get_last_row_id())


    def test_last_row_id_with_insert(self):
        tinyAPI.dsh().query(
            '''insert into unit_test_table(
                  value)
               values(
                  %s)''',
            [99881122])
        self.assertIsNotNone(tinyAPI.dsh().get_last_row_id())

        record = tinyAPI.dsh().one(
            """select value
                 from unit_test_table
                where id = %s""",
            [tinyAPI.dsh().get_last_row_id()])
        self.assertEqual(99881122, record['value'])


    def test_native_conversion_of_time_columns(self):
        tinyAPI.dsh().query(
            '''insert into unit_test_table(
                value,
                ti)
               values(
                %s,
                %s)''',
            [12345, '08:30:00']
        )

        record = tinyAPI.dsh().one(
            """select ti
                 from unit_test_table
                where value = %s""",
            [12345]
        )
        self.assertIsNotNone(record)
        self.assertIsInstance(record['ti'], datetime.time)
        self.assertEqual('08:30:00', str(record['ti']))


    def test_ping(self):
        self.assertEqual(
            1,
            tinyAPI.dsh().count(
                """select 1
                     from dual"""
            )
        )

        tinyAPI.dsh().ping()

        self.assertEqual(
            2,
            tinyAPI.dsh().count(
                """select 2
                     from dual"""
            )
        )


    def test_create_with_binary(self):
        id = tinyAPI.dsh().create(
            'unit_test_table',
            {'value': 123,
             '_binary message': 'abc def ghi'}
        )
        self.assertIsNotNone(id)

        record = tinyAPI.dsh().one(
            """select value,
                      message
                 from unit_test_table
                where id = %s""",
            [id]
        )
        self.assertIsNotNone(record)
        self.assertEqual(123, record['value'])
        self.assertEqual('abc def ghi', record['message'].decode())


    def test_auto_reconnect(self):
        connection_id = tinyAPI.dsh().connection_id()
        self.assertIsNotNone(connection_id)

        dsh_1 = \
            provider.autonomous_tx_start(
                ConfigManager().value('default unit test connection'),
                'tinyAPI'
            )
        dsh_1.query('kill {}'.format(connection_id))
        provider.autonomous_tx_stop_commit(dsh_1)

        records = tinyAPI.dsh().query('select 1 from dual')
        self.assertEqual(1, len(records))

# ----- Main ------------------------------------------------------------------

if __name__ == '__main__':
    unittest.main()
