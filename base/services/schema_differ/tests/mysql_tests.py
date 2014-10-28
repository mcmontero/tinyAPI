# ----- Info ------------------------------------------------------------------

__author__ = 'Michael Montero <mcmontero@gmail.com>'

# ----- Imports ---------------------------------------------------------------

from tinyAPI.base.services.schema_differ.mysql import SchemaDiffer

import tinyAPI
import unittest

# ----- Tests -----------------------------------------------------------------

class SchemaDifferMySQLTestCase(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super(SchemaDifferMySQLTestCase, self).__init__(*args, **kwargs)

        self.__differ = SchemaDiffer('local', 'schema_differ_source',
                                     'local', 'schema_differ_target') \
                            .dont_write_upgrade_scripts() \
                            .execute()


    def test_there_are_differences(self):
        self.assertTrue(self.__differ.there_are_differences())


    def test_ref_tables_to_create(self):
        tables = self.__differ.get_ref_tables_to_create()
        self.assertEqual(1, len(tables))
        self.assertEqual('schema_differ_ref_add', tables[0])


    def test_ref_tables_to_drop(self):
        tables = self.__differ.get_ref_tables_to_drop()
        self.assertEqual(1, len(tables))
        self.assertEqual('schema_differ_ref_drop', tables[0])


    def test_tables_to_create(self):
        tables = self.__differ.get_tables_to_create()
        self.assertEqual(1, len(tables))
        self.assertEqual('schema_differ_add', tables[0])


    def test_tables_to_drop(self):
        tables = self.__differ.get_tables_to_drop()
        self.assertEqual(1, len(tables))
        self.assertEqual('schema_differ_drop', tables[0])


    def test_columns_to_create(self):
        columns = self.__differ.get_columns_to_create()
        self.assertEqual(1, len(columns))
        self.assertEqual('schema_differ_cols.col_c', columns[0])


    def test_columns_to_drop(self):
        columns = self.__differ.get_columns_to_drop()
        self.assertEqual(1, len(columns))
        self.assertEqual('schema_differ_cols.col_z', columns[0])


    def test_columns_to_modify(self):
        columns = self.__differ.get_columns_to_modify()
        self.assertEqual(1, len(columns))
        self.assertTrue('schema_differ_cols.col_b' in columns)


    def test_foreign_keys_to_create(self):
        fks = self.__differ.get_foreign_keys_to_create()
        self.assertEqual(2, len(fks))
        self.assertEqual('schema_differ_fks_0_fk', fks[0]['name'])
        self.assertEqual('schema_differ_fks_1_fk', fks[1]['name'])


    def test_foreign_keys_to_drop(self):
        fks = self.__differ.get_foreign_keys_to_drop()
        self.assertEqual(2, len(fks))
        self.assertEqual('schema_differ_fks_100_fk', fks[0]['name'])
        self.assertEqual('schema_differ_fks_1_fk', fks[1]['name'])


    def test_ref_data_to_add(self):
        data = self.__differ.get_ref_data_to_add()
        self.assertEqual(1, len(data))
        self.assertEqual('schema_differ_ref_modify', data[0][0])
        self.assertEqual(1, data[0][1])


    def test_ref_data_to_modify(self):
        data = self.__differ.get_ref_data_to_modify()
        self.assertEqual(1, len(data))
        self.assertEqual('schema_differ_ref_modify', data[0][0])
        self.assertEqual(2, data[0][1])


    def test_ref_data_to_remove(self):
        data = self.__differ.get_ref_data_to_remove()
        self.assertEqual(1, len(data))
        self.assertEqual('schema_differ_ref_modify', data[0][0])
        self.assertEqual(3, data[0][1])


    def test_indexes_to_create(self):
        indexes = self.__differ.get_indexes_to_create()
        self.assertEqual(2, len(indexes))
        self.assertEqual('schema_differ_add_1_idx', indexes[0]['index_name'])
        self.assertEqual('schema_differ_mod_2_idx', indexes[1]['index_name'])


    def test_indexes_to_drop(self):
        indexes = self.__differ.get_indexes_to_drop()
        self.assertEqual(2, len(indexes))
        self.assertEqual('schema_differ_drop_3_idx', indexes[0]['index_name'])
        self.assertEqual('schema_differ_mod_2_idx', indexes[1]['index_name'])


    def test_unique_keys_to_create(self):
        uks = self.__differ.get_unique_keys_to_create()
        self.assertEqual(2, len(uks))
        self.assertEqual('schema_differ_add_1_uk', uks[0]['name'])
        self.assertEqual('schema_differ_mod_2_uk', uks[1]['name'])


    def test_unique_keys_to_drop(self):
        uks = self.__differ.get_unique_keys_to_drop()
        self.assertEqual(2, len(uks))
        self.assertEqual('schema_differ_drop_3_uk', uks[0]['name'])
        self.assertEqual('schema_differ_mod_2_uk', uks[1]['name'])


    def test_column_uniqueness_to_drop(self):
        cols = self.__differ.get_column_uniqueness_to_drop()
        self.assertEqual(2, len(cols))
        self.assertTrue('schema_differ_cols.col_b' in cols)
        self.assertTrue('schema_differ_remove_uk.value' in cols)

# ----- Main ------------------------------------------------------------------

if __name__ == '__main__':
    unittest.main()
