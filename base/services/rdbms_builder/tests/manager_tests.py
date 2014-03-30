# ----- Info ------------------------------------------------------------------

__author__ = 'Michael Montero <mcmontero@gmail.com>'

# ----- Import ----------------------------------------------------------------

from tinyAPI.base.services.rdbms_builder.manager import _RDBMSBuilderModuleSQL

import tinyAPI
import unittest

# ----- Test  -----------------------------------------------------------------

class RDBMSBuilderManagerTestCase(unittest.TestCase):

    def test_builder_module_basics(self):
        module = _RDBMSBuilderModuleSQL('abc', 'def')

        self.assertEqual('abc', module.get_name())
        self.assertEqual('def', module.get_prefix())


    def test_builder_module_dml_files(self):
        module = _RDBMSBuilderModuleSQL('abc', 'def')
        module.add_dml_file('a')
        module.add_dml_file('b')

        dml_files = module.get_dml_files()
        self.assertEqual(2, len(dml_files))
        self.assertEqual('a', dml_files[0])
        self.assertEqual('b', dml_files[1])


    def test_builder_module_build_file(self):
        module = _RDBMSBuilderModuleSQL('abc', 'def')
        module.set_build_file('/a/b/c')

        self.assertEqual('/a/b/c', module.get_build_file())


    def test_adding_definition(self):
        module = _RDBMSBuilderModuleSQL('abc', 'def')
        module.add_definition('a', 'b')
        module.add_definition('c', 'd')

        statements = module.get_definitions()
        self.assertEqual(2, len(statements))
        self.assertEqual('a', statements[0][0])
        self.assertEqual('b', statements[0][1])
        self.assertEqual('c', statements[1][0])
        self.assertEqual('d', statements[1][1])


    def test_adding_index(self):
        module = _RDBMSBuilderModuleSQL('abc', 'def')
        module.add_index('a', 'b')
        module.add_index('c', 'd')

        indexes = module.get_indexes()
        self.assertEqual(2, len(indexes))
        self.assertEqual('a', indexes[0][0])
        self.assertEqual('b', indexes[0][1])
        self.assertEqual('c', indexes[1][0])
        self.assertEqual('d', indexes[1][1])


    def test_adding_insert(self):
        module = _RDBMSBuilderModuleSQL('abc', 'def')
        module.add_insert('a', 'b')
        module.add_insert('c', 'd')

        inserts = module.get_inserts()
        self.assertEqual(2, len(inserts))
        self.assertEqual('a', inserts[0][0])
        self.assertEqual('b', inserts[0][1])
        self.assertEqual('c', inserts[1][0])
        self.assertEqual('d', inserts[1][1])

# ----- Main ------------------------------------------------------------------

if __name__ == '__main__':
    unittest.main()
