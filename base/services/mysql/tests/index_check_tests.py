# ----- Info ------------------------------------------------------------------

__author__ = 'Michael Montero <mcmontero@gmail.com>'

# ----- Imports ---------------------------------------------------------------

from tinyAPI.base.data_store.provider import DataStoreMySQL
from tinyAPI.base.services.mysql.index_check import MySQLIndexUsageParser
from tinyAPI.base.services.unit_testing import TransactionalDataStoreTestCase


import tinyAPI
import unittest

# ----- Test  -----------------------------------------------------------------

class IndexCheckTestCase(TransactionalDataStoreTestCase):

    def test_execute(self):
        parser = \
            MySQLIndexUsageParser() \
                .execute(
                    '# Using password on the command line is bad.\n# Executing now\n# The following index for table abc.def contains the clustered index and might be redundant:\n#\nCREATE UNIQUE INDEX `abc_def_uk` ON `db`.`def` (`col_a`, `col_b`) USING BTREE\n# The following index is a duplicate or redundant for table abc.def:\n#\nCREATE INDEX `abc_def_idx` ON `db`.`def` (`col_a`) USING BTREE\n#     may be redundant or duplicate of:\nCREATE UNIQUE INDEX `ghi_jkl_idx` ON `db`.`def` (`col_a`, `col_b`) USING BTREE\n# The following indexes for table core.channel_upon_reg contain the clustered index and might be redundant:\n#\nCREATE UNIQUE INDEX `mno_pqr_uk` ON `db`.`stu` (`col_a`, `col_b`, `col_c`) USING BTREE\n#\nALTER TABLE `db`.`abc` ADD PRIMARY KEY (`col_d`, `col_e`, `col_f`)'
                        .encode()
                )

        self.assertEqual(
            [
                ['abc_def_uk', '(col_a, col_b)'],
                ['mno_pqr_uk', '(col_a, col_b, col_c)'],
                ['abc_pk', '(col_d, col_e, col_f)']
            ],
            parser.clustered_indexes
        )
        self.assertEqual(
            [
                ['abc_def_idx', '(col_a)', 'ghi_jkl_idx', '(col_a, col_b)']
            ],
            parser.redundant_indexes
        )

# ----- Main ------------------------------------------------------------------

if __name__ == '__main__':
    unittest.main()
