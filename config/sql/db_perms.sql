grant all privileges
       on schema_differ_source.*
       to ''@'localhost';

grant all privileges
       on schema_differ_target.*
       to ''@'localhost';

grant all privileges
       on tinyAPI.*
       to ''@'localhost';

flush privileges;
