/*
+------------------------------------------------------------+
| SOURCE SCHEMA                                              |
+------------------------------------------------------------+
*/

drop database if exists schema_differ_source;
create database if not exists schema_differ_source;

/*
+------------------------------------------------------------+
| TARGET SCHEMA                                              |
+------------------------------------------------------------+
*/

drop database if exists schema_differ_target;
create database if not exists schema_differ_target;

/*
+------------------------------------------------------------+
| UNIT TEST SCHEMA                                           |
+------------------------------------------------------------+
*/

drop database if exists tinyAPI;
create database if not exists tinyAPI;
