#!/usr/bin/env /usr/bin/python3

# ----- Imports ---------------------------------------------------------------

import tinyAPI

from tinyAPI.base.services.cli import cli_main

# ----- Main ------------------------------------------------------------------

def main(cli):
    '''Executes an example of a RDBMS duplicate key exception.'''
    cli.header('Duplicate Key - RDBMS')

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
    tinyAPI.dsh().create(
        'a_table',
        {'id': 1, 'value': 1})

    cli.notice('The next record is a duplicate...')
    tinyAPI.dsh().create(
        'a_table',
        {'id': 1, 'value': 1})

# ----- Instructions ----------------------------------------------------------

cli_main(main)
