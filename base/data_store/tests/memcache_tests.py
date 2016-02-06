# ----- Info ------------------------------------------------------------------

__author__ = 'Michael Montero <mcmontero@gmail.com>'

# ----- Imports ---------------------------------------------------------------

from tinyAPI.base.config import ConfigManager

import mock
import tinyAPI
import unittest

# ----- Tests -----------------------------------------------------------------

class MemcacheTestCase(unittest.TestCase):

    def setUp(self):
        if ConfigManager().value('data store') == 'mysql':
            tinyAPI.dsh.select_db('local', 'tinyAPI')


    def test_cached_data(self):
        patcher_1 = mock.patch('tinyAPI.base.data_store.memcache.pylibmc')
        patcher_2 = mock.patch('tinyAPI.base.data_store.provider.Context')

        memcache = patcher_1.start()
        context = patcher_2.start()

        client = mock.Mock()
        memcache.Client.return_value = client
        context.env_unit_test.return_value = False

        for i in range(2):
            tinyAPI.dsh() \
                .memcache(
                    'test_memcache_cache', 180) \
                .query(
                    """select 1
                         from dual""")

        self.assertEqual(1, client.get.call_count)
        tinyAPI.dsh().close()

        tinyAPI.dsh() \
            .memcache(
                'test_memcache_cache', 180) \
            .query(
                """select 1
                     from dual""")

        self.assertEqual(2, client.get.call_count)

        patcher_1.stop()
        patcher_2.stop()

# ----- Main ------------------------------------------------------------------

if __name__ == '__main__':
    unittest.main()
