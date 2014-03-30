# ----- Info ------------------------------------------------------------------

__author__ = 'Michael Montero <mcmontero@gmail.com>'

# ----- Import ----------------------------------------------------------------

from tinyAPI.base.config import ConfigManager
import tinyAPI
import unittest

# ----- Tests -----------------------------------------------------------------

class ProviderMySQLTestCase(unittest.TestCase):

    def setUp(self):
        self.__execute_tests = False
        if ConfigManager().value('data store') == 'mysql':
            self.__execute_tests = True

            tinyAPI.dsh().select_db('local', 'test')
            tinyAPI.dsh().query('create database if not exists tinyAPI')

            tinyAPI.dsh().select_db('local', 'tinyAPI')
            tinyAPI.dsh().query(
                '''create table if not exists unit_test_table
                   (
                        id integer not null auto_increment primary key,
                        value integer not null
                   )''')


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

# ----- Main ------------------------------------------------------------------

if __name__ == '__main__':
    unittest.main()
