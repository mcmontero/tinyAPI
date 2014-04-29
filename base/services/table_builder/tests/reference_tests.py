# ----- Info ------------------------------------------------------------------

__author__ = 'Michael Montero <mcmontero@gmail.com>'

# ----- Imports ---------------------------------------------------------------

from tinyAPI.base.config import ConfigManager
import tinyAPI
import unittest

# ----- Tests -----------------------------------------------------------------

class TableBuilderReferenceTestCase(unittest.TestCase):

    def setUp(self):
        self.__execute_tests = False
        if len(ConfigManager().value('rdbms builder schemas')) > 0 and \
           ConfigManager().value('reference definition file') is not None:
            self.__execute_tests = True


    def test_getting_entire_table(self):
        if self.__execute_tests is True:
            table = tinyAPI.refv('tinyAPI_ref_unit_test')
            self.assertEqual(3, len(table))
            self.assertEqual('one', table[1])
            self.assertEqual('two', table[2])
            self.assertEqual('three', table[3])


    def test_encoding(self):
        if self.__execute_tests is True:
            self.assertEqual(1, tinyAPI.refv('tinyAPI_ref_unit_test', 'one'))


    def test_decoding(self):
        if self.__execute_tests is True:
            self.assertEqual('one', tinyAPI.refv('tinyAPI_ref_unit_test', 1))


    def test_invalid_value(self):
        if self.__execute_tests is True:
            self.assertIsNone(tinyAPI.refv('tinyAPI_ref_unit_test', -1))

# ----- Main ------------------------------------------------------------------

if __name__ == '__main__':
    unittest.main()
