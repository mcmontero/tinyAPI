# ----- Info ------------------------------------------------------------------

__author__ = 'Michael Montero <mcmontero@gmail.com>'

# ----- Imports ---------------------------------------------------------------

from tinyAPI.base.config import ConfigManager
from tinyAPI.base.data_store.exception import DataStoreException
import tinyAPI
import tinyAPI.base.data_store.provider as provider
import unittest

# ----- Tests -----------------------------------------------------------------

class ProviderMySQLTestCase(unittest.TestCase):

    def setUp(self):
        self.__execute_tests = False
        if ConfigManager().value('data store') == 'mysql':
            self.__execute_tests = True

            #tinyAPI.dsh().select_db('local', 'test')
            #tinyAPI.dsh().query('create database if not exists tinyAPI')

            #tinyAPI.dsh().select_db('local', 'tinyAPI')
            #tinyAPI.dsh().query(
                #'''create table if not exists tinyAPI.unit_test_table
                   #(
                        #id integer not null auto_increment primary key,
                        #value integer not null
                   #)''')


    def tearDown(self):
        if self.__execute_tests is True:
            tinyAPI.dsh().query('delete from unit_test_table')


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


    def test_two_active_data_store_handles(self):
        dsh_1 = provider.DataStoreMySQL()
        dsh_2 = provider.DataStoreMySQL()

        dsh_1.select_db('local', 'tinyAPI')
        dsh_2.select_db('local', 'tinyAPI')

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

        dsh_1.commit()
        dsh_2.commit()

        dsh_1.close()
        dsh_2.close()


    def test_asserting_is_dsh_errors(self):
        try:
            provider.assert_is_dsh('abc')

            self.fail('Was able to assert is DSH even though the value '
                      + 'provided was not instance of __DataStoreBase')
        except DataStoreException as e:
            self.assertEqual(
                'provided value is not instance of __DataStoreBase',
                e.get_message())


    def test_use_of_autonomous_transactions(self):
        dsh_1 = provider.autonomous_tx_start('local', 'tinyAPI')
        dsh_2 = provider.autonomous_tx_start('local', 'tinyAPI')

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

# ----- Main ------------------------------------------------------------------

if __name__ == '__main__':
    unittest.main()
