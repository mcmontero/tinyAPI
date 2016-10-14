# ----- Info ------------------------------------------------------------------

__author__ = 'Michael Montero <mcmontero@gmail.com>'

# ----- Imports ---------------------------------------------------------------

from tinyAPI.base.data_store.exception import DataStoreException
from tinyAPI.base.data_store.Randomizer import Randomizer

import tinyAPI
import unittest

# ----- Tests -----------------------------------------------------------------

class MemcacheTestCase(unittest.TestCase):

    def test_no_hosts(self):
        try:
            Randomizer([]).next()

            self.fail('Was able to get next even though no hosts were '
                      + 'configured.')
        except DataStoreException as e:
            self.assertEqual('no more hosts remain', e.message)

    def test_single_host(self):
        durability = Randomizer([['a', 'b', 'c']])

        self.assertEqual(['a', 'b', 'c'], durability.next())

        try:
            durability.next()

            self.fail('Was able to get next even though no more hosts remain.')
        except DataStoreException as e:
            self.assertEqual('no more hosts remain', e.message)

    def test_multiple_hosts(self):
        durability = Randomizer([['a', 'b', 'c'], ['d', 'e', 'f']])

        host, username, password = durability.next()
        if host == 'a':
            self.assertEqual('a', host)
            self.assertEqual('b', username)
            self.assertEqual('c', password)

            host, username, password = durability.next()

            self.assertEqual('d', host)
            self.assertEqual('e', username)
            self.assertEqual('f', password)

            try:
                durability.next()

                self.fail('Was able to get next host even though no more '
                          + 'hosts remain.')
            except DataStoreException as e:
                self.assertEqual('no more hosts remain', e.message)
        elif host == 'd':
            self.assertEqual('d', host)
            self.assertEqual('e', username)
            self.assertEqual('f', password)

            host, username, password = durability.next()

            self.assertEqual('a', host)
            self.assertEqual('b', username)
            self.assertEqual('c', password)

            try:
                durability.next()

                self.fail('Was able to get next host even though no more '
                          + 'hosts remain.')
            except DataStoreException as e:
                self.assertEqual('no more hosts remain', e.message)
        else:
            self.fail('unexpected host "{}"'.format(host))

# ----- Main ------------------------------------------------------------------

if __name__ == '__main__':
    unittest.main()
