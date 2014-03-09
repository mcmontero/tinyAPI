'''crypto_tests.py -- Unit tests for cryptographic functionality.'''

__author__ = 'Michael Montero <mcmontero@gmail.com>'

# ----- Import ---------------------------------------------------------------

from tinyAPI.base.config import ConfigManager
from tinyAPI.base.exception import ConfigurationException
import tinyAPI
import unittest

# ----- Tests ----------------------------------------------------------------

class ConfigTestCase(unittest.TestCase):

    def test_getting_a_value_exceptions(self):
        try:
            ConfigManager().value('no-such-option')

            self.fail('Was able to get a configuration value for a key that '
                      + 'is invalid.')
        except ConfigurationException as e:
            self.assertEqual(
                '"no-such-option" is not configured in tinyAPI_config',
                e.get_message())

# ----- Main -----------------------------------------------------------------

if __name__ == '__main__':
    unittest.main()
