'''utils_tests.py -- Unit tests for utilities.'''

__author__ = 'Michael Montero <mcmontero@gmail.com>'

# ----- Import ----------------------------------------------------------------

from tinyAPI.base.utils import find_dirs, find_files
import tinyAPI
import unittest

# ----- Tests -----------------------------------------------------------------

class UtilsTestCase(unittest.TestCase):

    def test_find_files(self):
        files = find_files('/opt/tinyAPI/*', 'no-such-files')
        self.assertEqual(0, len(files))

        files = find_files('/opt/tinyAPI/*', 'tinyAPI_config.py')
        self.assertEqual(1, len(files))
        self.assertEqual('/opt/tinyAPI/config/tinyAPI_config.py', files[0])

    def test_find_dirs(self):
        dirs = find_dirs('/opt/tinyAPI/*', 'no-such-dirs')
        self.assertEqual(0, len(dirs))

        dirs = find_dirs('/opt/tinyAPI/*', 'base')
        self.assertEqual(1, len(dirs))
        self.assertEqual('/opt/tinyAPI/base', dirs[0])

# ----- Main ------------------------------------------------------------------

if __name__ == '__main__':
    unittest.main()
