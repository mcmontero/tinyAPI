#!/usr/bin/env python3

# ----- Imports ---------------------------------------------------------------

import tinyAPI

# ----- Instructions ----------------------------------------------------------

table = tinyAPI.Table('core', 'test_table') \
            .serial() \
            .bin('col_a', 200, True) \
            .bit('col_b', True, 8) \
            .bint('col_c', True, 50) \
            .blob('col_d', 200, True) \
            .bool('col_e', True) \
            .char('col_f', 20, True) \
            .dec('col_g', True, 10, 7) \
                .defv(123.45) \
            .double('col_h', True, 11, 8) \
            .dt('col_i', True) \
            .dtt('col_j', True) \
            .enum('col_k', [1, 2, 3], True) \
            .fixed('col_l', True, 12, 9) \
            .float('col_m', True, 13) \
            .int('col_n', True, 14) \
            .lblob('col_o', True) \
            .ltext('col_p', True) \
            .mblob('col_q', True) \
            .mint('col_r', True, 15) \
                .uk() \
            .mtext('col_s', True) \
            .set('col_t', ['a', 'b', 'c'], True) \
            .sint('col_u', True, 16) \
            .tblob('col_v', True) \
            .text('col_w', True, 17) \
            .ti('col_x', True) \
            .tint('col_y', True, 18) \
            .ts('col_z', True) \
            .ttext('col_1', True) \
            .vbin('col_2', 200, True) \
            .vchar('col_3', 300, True) \
            .yr('col_4', True, 2) \
            .updated() \
            .created() \
            .idx(['col_a', 'col_b']) \
            .idx(['col_c'])

print(table.get_definition())
print()

indexes = table.get_index_definitions()
for index in indexes:
    print(index + "\n")
