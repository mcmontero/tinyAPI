# ----- Info ------------------------------------------------------------------

__author__ = 'Michael Montero <mcmontero@gmail.com>'

# ----- Imports ---------------------------------------------------------------

from tinyAPI.base.data_store.MySQL import MySQL

import tinyAPI
import unittest

# ----- Tests -----------------------------------------------------------------

class TestCase(unittest.TestCase):

    def test_dissociate_dont_key_on_first(self):
        self.assertEqual(
            [
                ['1', '2', '3'],
                ['4', '5', '6']
            ],
            MySQL().dissociate('1^2^3`4^5^6', '`', '^')
        )


    def test_dissociate_key_on_first(self):
        self.assertEqual(
            {
                '1': ['2', '3'],
                '4': ['5', '6']
            },
            MySQL().dissociate('1}{2}{3`4}{5}{6', '`', '}{', True)
        )

# ----- Main ------------------------------------------------------------------

if __name__ == '__main__':
    unittest.main()
