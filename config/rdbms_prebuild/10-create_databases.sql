/*
+------------------------------------------------------------+
| SOURCE SCHEMA                                              |
+------------------------------------------------------------+
*/

drop database if exists schema_differ_source;
create database if not exists schema_differ_source;

     grant all privileges
        on schema_differ_source.*
        to ''@'localhost'
identified by '';

/*
+------------------------------------------------------------+
| TARGET SCHEMA                                              |
+------------------------------------------------------------+
*/

drop database if exists schema_differ_target;
create database if not exists schema_differ_target;

     grant all privileges
        on schema_differ_target.*
        to ''@'localhost'
identified by '';

flush privileges;

/*
+------------------------------------------------------------+
| UNIT TEST DATABASE                                         |
+------------------------------------------------------------+
*/

drop database if exists tinyAPI;
create data if not exists tinyAPI;

     grant all privileges
        on tinyAPI.*
        to ''@'localhost'
identified by '';

flush privileges;


