'''crypto_tests.py -- Unit tests for cryptographic functionality.'''

__author__ = 'Michael Montero <mcmontero@gmail.com>'

# ----- Import ---------------------------------------------------------------

from tinyAPI.base.services.crypto import DataArmor
from tinyAPI.base.services.exception import CryptoException
import tinyAPI
import unittest

# ----- Tests ----------------------------------------------------------------

class CryptoTestCase(unittest.TestCase):

    def test_data_armor_exceptions(self):
        try:
            DataArmor('123', [])

            self.fail('Was able to instantiate DataArmor even though the key '
                      + 'provided was too short.')
        except CryptoException as e:
            self.assertEqual(
                'key must be of length 16, 24, or 32 bytes',
                e.get_message())

    def test_encrypting_decrypting(self):
        key = '12345678901234567890123456789012'
        string = 'hello world!'

        token = DataArmor(key, string).lock()
        self.assertIsNotNone(token)

        self.assertEqual(string, DataArmor(key, token).unlock())

    def test_modifying_token(self):
        key = '12345678901234567890123456789012'
        string = 'hello world!'

        token = DataArmor(key, string).lock()

        try:
            DataArmor(key, token[:-1]).unlock()

            self.fail('Was able to unlock token even though it was modified.')
        except CryptoException as e:
            self.assertEqual('armored token has been tampered with',
                             e.get_message())

# ----- Main -----------------------------------------------------------------

if __name__ == '__main__':
    unittest.main()
