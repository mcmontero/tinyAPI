#!/usr/bin/env python3

# ----- Imports --------------------------------------------------------------

import tinyAPI

# ----- Instructions ---------------------------------------------------------

table = tinyAPI.Table('core', 'test_table') \
            .serial()

print(table.get_definition())
