#!/usr/bin/env python3

# ----- Imports ---------------------------------------------------------------

import tinyAPI

# ----- Instructions ----------------------------------------------------------

ref_table = tinyAPI.RefTable('core', 'test_ref_table') \
                .add(1, 'abc') \
                .add(2, 'def')

print(ref_table.get_definition() + "\n")

inserts = ref_table.get_insert_statements()
for statement in inserts:
    print(statement + "\n")
