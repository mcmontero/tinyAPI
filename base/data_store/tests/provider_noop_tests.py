# ----- Info ------------------------------------------------------------------

__author__ = 'Michael Montero <mcmontero@gmail.com>'

# ----- Imports ---------------------------------------------------------------

from tinyAPI.base.data_store.provider import DataStoreNOOP

import tinyAPI
import tinyAPI.base.data_store.provider as provider
import unittest

# ----- Tests -----------------------------------------------------------------

class ProviderNOOPTestCase(unittest.TestCase):

    def test_unsupported_operations(self):
        self.assertIsNone(DataStoreNOOP().query('select 1 from dual'))
        self.assertEqual(0, DataStoreNOOP().requests)


    def test_supported_operations_no_errors(self):
        DataStoreNOOP().close()
        DataStoreNOOP().commit()
        DataStoreNOOP().commit(True)
        DataStoreNOOP().rollback()
        DataStoreNOOP().rollback(True)

# ----- Main ------------------------------------------------------------------

if __name__ == '__main__':
    unittest.main()
