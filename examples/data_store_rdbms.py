#!/usr/bin/env python3

# ----- Imports --------------------------------------------------------------

import tinyAPI
from tinyAPI.base.services.cli import cli_main

# ----- Main -----------------------------------------------------------------

def main(cli):
    '''Executes examples of all the ways in which you can use the data store
       sub-system for interacting with an RDBMS.'''
    cli.header('Data Store - RDBMS')

    '''Select the named database you wish to connect to.  In this case, "local"
       is one of the connection names defined in tinyAPI_config.py.  "tinyAPI"
       is the name of the schema you wish to connect to.'''
    tinyAPI.dsh().select_db('local', 'tinyAPI')

    cli.notice('Creating table called "a_table"...')
    tinyAPI.dsh().query(
        ('create table if not exists a_table('
         + 'id integer not null auto_increment primary key,'
         + 'value integer not null)')
    )

    cli.notice('Removing any records in a_table...')
    tinyAPI.dsh().query('delete from a_table')

    cli.notice('Added record to a_table...')
    for i in range(1, 5):
        id = tinyAPI.dsh().create(
                'a_table',
                {'value': i},
                True)
        cli.notice('created ID #' + str(id), 1)
    tinyAPI.dsh().commit()

    cli.notice('How many records did we just create?')
    cli.notice(str(tinyAPI.dsh().count('select count(*) from a_table')), 1)

    cli.notice('What is the ID for 3rd value?')
    record = tinyAPI.dsh().nth(2, 'select id from a_table');
    cli.notice(str(record['id']), 1)

    cli.notice('Update all records by multiplying value by 2.')
    tinyAPI.dsh().query(
        ('update a_table'
         + ' set value = value * 2'))
    tinyAPI.dsh().commit()

    cli.notice('Delete one of the records...')
    tinyAPI.dsh().delete(
        'a_table',
        {'value': 2})
    tinyAPI.dsh().commit()

    cli.notice('Get all of the remaining records...')
    records = tinyAPI.dsh().query(
        '''select id,
                  value
             from a_table
            order by id asc''')

    for record in records:
        cli.notice(str(record['id']) + ' = ' + str(record['value']), 1)

    cli.notice('Delete all of the records from a_table...')
    tinyAPI.dsh().delete('a_table')
    tinyAPI.dsh().commit()

    cli.notice('Drop a_table...')
    tinyAPI.dsh().query('drop table a_table')

# ----- Instructions ---------------------------------------------------------

cli_main(main)
