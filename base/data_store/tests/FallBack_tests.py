# ----- Info ------------------------------------------------------------------

__author__ = 'Michael Montero <mcmontero@gmail.com>'

# ----- Imports ---------------------------------------------------------------

from tinyAPI.base.data_store.exception import DataStoreException
from tinyAPI.base.data_store.FallBack import FallBack

import tinyAPI
import unittest

# ----- Tests -----------------------------------------------------------------

class MemcacheTestCase(unittest.TestCase):

    def test_no_hosts(self):
        try:
            FallBack([])

            self.fail('Was able to get next even though no hosts were '
                      + 'configured.')
        except DataStoreException as e:
            self.assertEqual('exactly 2 hosts must be configured', e.message)

    def test_one_host(self):
        try:
            FallBack([['a', 'b', 'c']])

            self.fail('Was able to get next even though no hosts were '
                      + 'configured.')
        except DataStoreException as e:
            self.assertEqual('exactly 2 hosts must be configured', e.message)

    def test_three_hosts(self):
        try:
            FallBack([['a', 'b', 'c'], ['d', 'e', 'f'], ['g', 'h', 'i']])

            self.fail('Was able to get next even though no hosts were '
                      + 'configured.')
        except DataStoreException as e:
            self.assertEqual('exactly 2 hosts must be configured', e.message)

    def test_next_always_select_primary(self):
        for i in range(20):
            self.assertEqual(
                ['a', 'b', 'c'],
                FallBack([['a', 'b', 'c'], ['d', 'e', 'f']]).next()
            )

    def test_fall_back(self):
        durability = FallBack([['a', 'b', 'c'], ['d', 'e', 'f']])

        self.assertEqual(['a', 'b', 'c'], durability.next())
        self.assertEqual(['d', 'e', 'f'], durability.next())

        try:
            self.assertEqual(['d', 'e', 'f'], durability.next())

            self.fail('Was able to get next even though no more hosts were '
                      + 'configured.')
        except DataStoreException as e:
            self.assertEqual('no more hosts remain', e.message)

# ----- Main ------------------------------------------------------------------

if __name__ == '__main__':
    unittest.main()
