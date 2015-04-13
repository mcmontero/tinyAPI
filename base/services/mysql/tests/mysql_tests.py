# ----- Info ------------------------------------------------------------------

__author__ = 'Michael Montero <mcmontero@gmail.com>'

# ----- Imports ---------------------------------------------------------------

from tinyAPI.base.data_store.provider import DataStoreMySQL
from tinyAPI.base.services.mysql.view import ViewFlipper
from tinyAPI.base.services.unit_testing import TransactionalDataStoreTestCase


import tinyAPI
import unittest

# ----- Test  -----------------------------------------------------------------

class MySQLTestCase(TransactionalDataStoreTestCase):

    def test_view_flipper(self):
        mysql = DataStoreMySQL()
        mysql.select_db('local', 'tinyAPI')

        mysql.query(
            "create table if not exists "
            + "schema_differ_source.unit_test_view_flipper_1(id int)")
        mysql.query(
            "create table if not exists "
            + "schema_differ_source.unit_test_view_flipper_2(id int)")
        mysql.query(
            """create or replace view
                   schema_differ_source.unit_test_view_flipper
                    as select *
                         from schema_differ_source.unit_test_view_flipper_2""")

        vf = ViewFlipper('unit_test_view_flipper')
        self.assertEqual(
            'unit_test_view_flipper_2', vf.get_active_table_name())
        self.assertEqual(
            'unit_test_view_flipper_1', vf.get_inactive_table_name())

        vf.execute()

        vf = ViewFlipper('unit_test_view_flipper')
        self.assertEqual(
            'unit_test_view_flipper_1', vf.get_active_table_name())
        self.assertEqual(
            'unit_test_view_flipper_2', vf.get_inactive_table_name())
        vf.execute()

        vf = ViewFlipper('unit_test_view_flipper')
        self.assertEqual(
            'unit_test_view_flipper_2', vf.get_active_table_name())
        self.assertEqual(
            'unit_test_view_flipper_1', vf.get_inactive_table_name())

        mysql.query("drop view schema_differ_source.unit_test_view_flipper")
        mysql.query("drop table schema_differ_source.unit_test_view_flipper_1")
        mysql.query("drop table schema_differ_source.unit_test_view_flipper_2")

# ----- Main ------------------------------------------------------------------

if __name__ == '__main__':
    unittest.main()
