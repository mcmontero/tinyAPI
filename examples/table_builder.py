#!/usr/bin/env python3

# ----- Imports --------------------------------------------------------------

import tinyAPI

# ----- Build ----------------------------------------------------------------

def test_build():
    return [
        tinyAPI.Table('core', 'test_table')
            .int('id'),

        tinyAPI.Table('core', 'test_table_2')
            .int('id')
    ]

# ----- Instructions ---------------------------------------------------------

print(test_build())
