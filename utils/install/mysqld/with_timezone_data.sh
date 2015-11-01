#!/bin/bash

/bin/echo "Starting mysqld..."
/etc/init.d/mysqld start

/bin/echo "Installing timezone data..."
/usr/bin/mysql_tzinfo_to_sql /usr/share/zoneinfo \
    | /usr/bin/mysql -u root -D mysql
