# ----- Info ------------------------------------------------------------------

__author__ = 'Michael Montero <mcmontero@gmail.com>'

# ----- Imports ---------------------------------------------------------------

from tinyAPI.base.services.cli import CLIOutputRenderer

import tinyAPI
import unittest

# ----- Tests -----------------------------------------------------------------

class ServicesCLITestCase(unittest.TestCase):

    def test_CLIOutputRenderer_header(self):
        expected = '''# +--------------------------------------------------------------------------+
# | Test                                                                     |
# +--------------------------------------------------------------------------+
'''

        self.assertEqual(expected, CLIOutputRenderer.header('Test'))

# ----- Main ------------------------------------------------------------------

if __name__ == '__main__':
    unittest.main()
