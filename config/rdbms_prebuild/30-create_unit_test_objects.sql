/*
+------------------------------------------------------------+
| UNIT TEST SCHEMA                                           |
+------------------------------------------------------------+
*/

drop table if exists tinyAPI.unit_test_table;
create table tinyAPI.unit_test_table
(
    id integer not null auto_increment primary key,
    value integer not null
) engine = innodb default charset = utf8 collate = utf8_unicode_ci;
