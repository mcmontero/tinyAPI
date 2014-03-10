'''manager_tests.py -- Unit tests for the RDBMS Builder manager.'''

__author__ = 'Michael Montero <mcmontero@gmail.com>'

# ----- Import ---------------------------------------------------------------

from tinyAPI.base.services.rdbms_builder.manager import _RDBMSBuilderModule
import tinyAPI
import unittest

# ----- Test  ----------------------------------------------------------------

class RDBMSBuilderManagerTestCase(unittest.TestCase):

    def test_builder_module_basics(self):
        module = _RDBMSBuilderModule('abc', 'def')

        self.assertEqual('abc', module.get_name())
        self.assertEqual('def', module.get_prefix())

    def test_builder_module_dml_files(self):
        module = _RDBMSBuilderModule('abc', 'def')
        module.add_dml_file('a')
        module.add_dml_file('b')

        dml_files = module.get_dml_files()
        self.assertEqual(2, len(dml_files))
        self.assertEqual('a', dml_files[0])
        self.assertEqual('b', dml_files[1])

    def test_builder_module_build_file(self):
        module = _RDBMSBuilderModule('abc', 'def')
        module.set_build_file('/a/b/c')

        self.assertEqual('/a/b/c', module.get_build_file())

    def test_builder_module_sql(self):
        module = _RDBMSBuilderModule('abc', 'def')
        module.set_sql(['a', 'b'])

        sql = module.get_sql()
        self.assertEqual(2, len(sql))
        self.assertEqual('a', sql[0])
        self.assertEqual('b', sql[1])

# ----- Main -----------------------------------------------------------------

if __name__ == '__main__':
    unittest.main()
