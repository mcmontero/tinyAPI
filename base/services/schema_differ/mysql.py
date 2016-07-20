# ----- Info ------------------------------------------------------------------

__author__ = 'Michael Montero <mcmontero@gmail.com>'

# ----- Imports ---------------------------------------------------------------

from tinyAPI.base.config import ConfigManager
from tinyAPI.base.data_store.provider import DataStoreMySQL
from tinyAPI.base.services.mysql.index_check import MySQLIndexUsageParser

import os
import re
import subprocess

__all__ = [
    'SchemaDiffer'
]

# ----- Public Classes --------------------------------------------------------

class SchemaDiffer(object):
    '''Finds all of the schema differences between two MySQL databases.'''

    def __init__(self,
                 source_connection_name,
                 source_db_name,
                 target_connection_name,
                 target_db_name):
        self.__cli = None
        self.__source = None
        self.__target = None
        self.__source_db_name = None
        self.__target_db_name = None
        self.__ref_tables_to_create = None
        self.__ref_tables_to_drop = None
        self.__tables_to_create = None
        self.__tables_to_drop = None
        self.__table_create_drop_list = None
        self.__ref_table_drop_list = None
        self.__columns_to_create = None
        self.__columns_to_drop = None
        self.__columns_to_modify = None
        self.__column_uniqueness_to_drop = None
        self.__foreign_keys_to_create = None
        self.__foreign_keys_to_drop = None
        self.__ref_data_to_add = None
        self.__ref_data_to_remove = None
        self.__ref_data_to_modify = None
        self.__indexes_to_create = None
        self.__indexes_to_drop = None
        self.__unique_keys_to_create = None
        self.__unique_keys_to_drop = None
        self.__index_usage_parser = None

        self.__source = DataStoreMySQL()
        self.__source.select_db(source_connection_name, 'information_schema')
        self.__source_db_name = source_db_name

        self.__target = DataStoreMySQL()
        self.__target.select_db(target_connection_name, 'information_schema')
        self.__target_db_name = target_db_name

        self.__enable_write_upgrade_scripts = True


    def __compute_column_differences(self):
        self.__notice('Computing column differences...')

        query = \
            """select table_name,
                      column_name,
                      column_default,
                      is_nullable,
                      character_set_name,
                      collation_name,
                      column_type,
                      column_key,
                      extra
                 from columns
                where table_schema = %s
                  and table_name not like '%%\_ref\_%%'"""
        if self.__table_create_drop_list:
            query += ' and table_name not in (' \
                     + self.__table_create_drop_list \
                     + ')'

        source_columns = \
            self.__query_source(
                query,
                [self.__source_db_name])
        target_columns = \
            self.__query_target(
                query,
                [self.__target_db_name])

        source_names = []
        source = {}
        if source_columns:
            for source_column in source_columns:
                name = source_column['table_name'] \
                       + '.' \
                       + source_column['column_name']

                source_names.append(name)
                source[name] = source_column

        target_names = []
        target = {}
        if target_columns:
            for target_column in target_columns:
                name = target_column['table_name'] \
                       + '.' \
                       + target_column['column_name']

                target_names.append(name)
                target[name] = target_column


        self.__columns_to_create = \
            list(set(source_names).difference(target_names))
        for column in self.__columns_to_create:
            self.__notice('(+) ' + column, 1)

        self.__columns_to_drop = \
            list(set(target_names).difference(source_names))
        for column in self.__columns_to_drop:
            self.__notice('(-) ' + column, 1)

        self.__columns_to_modify = {}
        self.__column_uniqueness_to_drop = []
        for name, data in source.items():
            if name in self.__columns_to_create or \
               name in self.__columns_to_drop:
                continue;

            if name not in target.keys():
                raise SchemaDifferException(
                    'could not find column "' + name + '" in the list of '
                    + 'target columns')

            if data['column_key'] != 'UNI' and \
               target[name]['column_key'] == 'UNI':
                self.__notice('(-) ' + name + ' (uniqueness)', 1)

                self.__column_uniqueness_to_drop.append(name)

            for key, value in data.items():
                if target[name][key] != value and key != 'column_key':
                    self.__notice('(=) ' + name + ' (' + key + ')', 1)
                    self.__columns_to_modify[name] = data
                    break


    def __compute_foreign_key_differences(self):
        self.__notice('Computing foreign key differences...')

        query = \
            """select k.table_name,
                      k.column_name,
                      k.constraint_name,
                      k.ordinal_position,
                      k.referenced_table_name,
                      k.referenced_column_name,
                      c.delete_rule
                 from key_column_usage k
                 left outer join referential_constraints c
                   on c.constraint_schema = k.constraint_schema
                  and c.constraint_name = k.constraint_name
                  and k.constraint_name = k.constraint_name
                where k.constraint_schema = %s
                  and k.constraint_name like '%%\_fk'"""
        if self.__table_create_drop_list:
            query += ' and k.table_name not in (' \
                     + self.__table_create_drop_list \
                     + ')' \

        source_fks = \
            self.__process_fks(
                self.__query_source(
                    query,
                    [self.__source_db_name]))
        target_fks = \
            self.__process_fks(
                self.__query_target(
                    query,
                    [self.__target_db_name]))

        source_fk_names = source_fks.keys()
        target_fk_names = target_fks.keys()

        foreign_keys_to_create = \
            list(set(source_fk_names).difference(target_fk_names))
        foreign_keys_to_drop = \
            list(set(target_fk_names).difference(source_fk_names))

        self.__foreign_keys_to_create = []
        for name in foreign_keys_to_create:
            self.__notice('(+) ' + name, 1)

            self.__foreign_keys_to_create.append(source_fks[name])

        self.__foreign_keys_to_drop = []
        for name in foreign_keys_to_drop:
            self.__notice('(-) ' + name, 1)

            self.__foreign_keys_to_drop.append(target_fks[name])

        for name, fk in source_fks.items():
            if name in target_fks.keys() and \
               name not in self.__foreign_keys_to_create and \
               name not in self.__foreign_keys_to_drop:
                if source_fks[name]['table_name'] != \
                   target_fks[name]['table_name'] or \
                   source_fks[name]['ref_table_name'] != \
                   target_fks[name]['ref_table_name'] or \
                   source_fks[name]['delete_rule'] != \
                   target_fks[name]['delete_rule'] or \
                   ','.join(list(source_fks[name]['cols'].values())) != \
                   ','.join(list(target_fks[name]['cols'].values())) or \
                   ','.join(list(source_fks[name]['ref_cols'].values())) != \
                   ','.join(list(target_fks[name]['ref_cols'].values())):
                    self.__notice('(=) ' + name, 1)

                    self.__foreign_keys_to_drop.append(source_fks[name])
                    self.__foreign_keys_to_create.append(source_fks[name])


    def __compute_index_differences(self):
        self.__notice('Computing index differences...')

        query = \
            """select table_name,
                      index_name,
                      seq_in_index,
                      column_name
                 from statistics
                where index_schema = %s
                  and index_name like '%%\_idx'"""
        if self.__table_create_drop_list:
            query += ' and table_name not in (' \
                     + self.__table_create_drop_list \
                     + ')'

        source_indexes = \
            self.__query_source(
                query,
                [self.__source_db_name])
        target_indexes = \
            self.__query_target(
                query,
                [self.__target_db_name])

        source_names = []
        source = {}
        for index in source_indexes:
            source_names.append(index['index_name'])

            if index['index_name'] not in source:
                source[index['index_name']] = {
                    'table_name': index['table_name'],
                    'cols': []
                }

            source[index['index_name']]['cols'] \
                .insert(index['seq_in_index'], index['column_name'])

        target_names = []
        target = {}
        for index in target_indexes:
            target_names.append(index['index_name'])

            if index['index_name'] not in target:
                target[index['index_name']] = {
                    'table_name': index['table_name'],
                    'cols': []
                }

            target[index['index_name']]['cols'] \
                .insert(index['seq_in_index'], index['column_name'])


        indexes_to_create = \
            list(set(source_names).difference(target_names))
        indexes_to_drop = \
            list(set(target_names).difference(source_names))
        indexes_to_modify = \
            []

        for name, data in source.items():
            if name in target.keys() and \
               ','.join(data['cols']) != ','.join(target[name]['cols']):
                indexes_to_modify.append(name)

        self.__indexes_to_create = []
        for name in indexes_to_create:
            self.__notice('(+) ' + name, 1)

            self.__indexes_to_create.append({
                'table_name': source[name]['table_name'],
                'index_name': name,
                'cols': source[name]['cols']
            })

        self.__indexes_to_drop = []
        for name in indexes_to_drop:
            self.__notice('(-) ' + name, 1)

            self.__indexes_to_drop.append({
                'table_name': target[name]['table_name'],
                'index_name': name,
                'cols': target[name]['cols']
            })

        for name in indexes_to_modify:
            self.__notice('(=) ' + name, 1)

            self.__indexes_to_create.append({
                'table_name': source[name]['table_name'],
                'index_name': name,
                'cols': source[name]['cols']
            })

            self.__indexes_to_drop.append({
                'table_name': target[name]['table_name'],
                'index_name': name,
                'cols': target[name]['cols']
            })


    def __compute_ref_table_data_differences(self):
        self.__notice('Computing reference table data differences...')

        query = \
            """select table_name
                 from tables
                where table_schema = %s
                  and table_name like '%%\_ref\_%%'"""
        if self.__ref_table_drop_list:
            query += ' and table_name not in (' \
                     + self.__ref_table_drop_list \
                     + ')'

        source_tables = \
            self.__flatten_tables(
                self.__query_source(
                    query,
                    [self.__source_db_name]))
        target_tables = \
            self.__flatten_tables(
                self.__query_target(
                    query,
                    [self.__target_db_name]))

        source_data = {}
        for table in source_tables:
            source_data[table] = {}

            records = self.__query_source(
                '''select id,
                          value,
                          display_order
                     from ''' + self.__source_db_name + '.' + table + '''
                    order by id asc''')

            for record in records:
                source_data[table][record['id']] = [
                    str(record['value']),
                    str(record['display_order'])
                ]

        target_data = {}
        for table in target_tables:
            target_data[table] = {}

            records = self.__query_target(
                '''select id,
                          value,
                          display_order
                     from ''' + self.__target_db_name + '.' + table + '''
                    order by id asc''')

            for record in records:
                target_data[table][record['id']] = [
                    str(record['value']),
                    str(record['display_order'])
                ]

        self.__ref_data_to_add = []
        self.__ref_data_to_modify = []
        for table, data in source_data.items():
            for id, values in data.items():
                if table not in target_data or \
                   id not in target_data[table]:
                    self.__notice('(+) ' + table + ' #' + str(id), 1)

                    self.__ref_data_to_add.append([
                        table,
                        id,
                        values[0],
                        values[1]
                    ])
                else:
                    if ','.join(values) != ','.join(target_data[table][id]):
                        self.__notice('(=) ' + table + ' #' + str(id), 1)

                        self.__ref_data_to_modify.append([
                            table,
                            id,
                            values[0],
                            values[1]
                        ])

        self.__ref_data_to_remove = []
        for table, data in target_data.items():
            for id, values in data.items():
                if table not in source_data or \
                   id not in source_data[table]:
                    self.__notice('(-) ' + table + '#' + str(id), 1)

                    self.__ref_data_to_remove.append([
                        table,
                        id,
                        values[0],
                        values[1]
                    ])


    def __compute_ref_table_differences(self):
        self.__notice('Computing reference table differences...')

        query = \
            """select table_name
                 from tables
                where table_schema = %s
                  and table_name like '%%\_ref\_%%'"""

        source_tables = \
            self.__flatten_tables(
                self.__query_source(
                    query,
                    [self.__source_db_name]))
        target_tables = \
            self.__flatten_tables(
                self.__query_target(
                    query,
                    [self.__target_db_name]))

        self.__ref_tables_to_create = \
            list(set(source_tables).difference(target_tables))
        for table in self.__ref_tables_to_create:
            self.__notice('(+) ' + table, 1)

        drop_list = []

        self.__ref_tables_to_drop = \
            list(set(target_tables).difference(source_tables))
        for table in self.__ref_tables_to_drop:
            self.__notice('(-) ' + table, 1)
            drop_list.append("'" + table + "'")

        self.__ref_table_drop_list = ','.join(drop_list)


    def __compute_table_differences(self):
        self.__notice('Computing table differences...')

        create_drop_list = []

        query = \
            """select table_name
                 from tables
                where table_schema = %s
                  and table_name not like '%%\_ref\_%%'"""

        source_tables = \
            self.__flatten_tables(
                self.__query_source(
                    query,
                    [self.__source_db_name]))
        target_tables = \
            self.__flatten_tables(
                self.__query_target(
                    query,
                    [self.__target_db_name]))

        self.__tables_to_create = \
            list(set(source_tables).difference(target_tables))
        for table in self.__tables_to_create:
            self.__notice('(+) ' + table, 1)
            create_drop_list.append("'" + table + "'")

        self.__tables_to_drop = \
            list(set(target_tables).difference(source_tables))
        for table in self.__tables_to_drop:
            self.__notice('(-) ' + table, 1)
            create_drop_list.append("'" + table + "'")

        self.__table_create_drop_list = ','.join(create_drop_list)


    def __compute_unique_key_differences(self):
        self.__notice('Computing unique key differences...')

        query = \
            """select table_name,
                      constraint_name,
                      column_name,
                      ordinal_position
                 from key_column_usage
                where table_schema = %s
                  and constraint_name like '%%\_uk'"""
        if self.__table_create_drop_list:
            query += ' and table_name not in (' \
                     + self.__table_create_drop_list \
                     + ')'

        source_uks = \
            self.__process_uks(
                self.__query_source(
                    query,
                    [self.__source_db_name]))
        target_uks = \
            self.__process_uks(
                self.__query_target(
                    query,
                    [self.__target_db_name]))

        source_uk_names = source_uks.keys()
        target_uk_names = target_uks.keys()

        unique_keys_to_create = \
            list(set(source_uk_names).difference(target_uk_names))
        unique_keys_to_drop = \
            list(set(target_uk_names).difference(source_uk_names))

        self.__unique_keys_to_create = []
        for name in unique_keys_to_create:
            self.__notice('(+) ' + name, 1)
            self.__unique_keys_to_create.append(source_uks[name])

        self.__unique_keys_to_drop = []
        for name in unique_keys_to_drop:
            self.__notice('(-) ' + name, 1)
            self.__unique_keys_to_drop.append(target_uks[name])

        for name, uk in source_uks.items():
            if name in target_uks.keys() and \
               name not in unique_keys_to_create and \
               name not in unique_keys_to_drop:
                if source_uks[name]['table_name'] != \
                   target_uks[name]['table_name'] or \
                   ','.join(source_uks[name]['cols'].values()) != \
                   ','.join(target_uks[name]['cols'].values()):
                    self.__notice('(=) ' + name, 1)

                    self.__unique_keys_to_drop.append(source_uks[name])
                    self.__unique_keys_to_create.append(source_uks[name])


    def dont_write_upgrade_scripts(self):
        self.__enable_write_upgrade_scripts = False
        return self


    def __error(self, message, indent=None):
        if not self.__cli:
            return

        self.__cli.error(message, indent)


    def execute(self):
        self.__verify_schemas()

        self.__compute_ref_table_differences()
        self.__compute_table_differences()
        self.__compute_column_differences()
        self.__compute_foreign_key_differences()
        self.__compute_ref_table_data_differences()
        self.__compute_index_differences()
        self.__compute_unique_key_differences()
        self.__perform_index_check()

        if not self.there_are_differences():
            self.__notice('Both schemas are the same!')
            exit(0)

        self.__write_upgrade_scripts()

        self.__target.close()
        self.__source.close()

        return self


    def __flatten_tables(self, tables=tuple()):
        if not tables:
            return []

        results = []
        for table in tables:
            results.append(table['table_name'])

        return results


    def __get_column_terms(self, column_data):
        terms = []

        if column_data['extra'] is not None and \
           len(column_data['extra']) > 0:
            terms.append(column_data['extra'])

        if column_data['character_set_name']:
            terms.append('character set ' + column_data['character_set_name'])

        if column_data['collation_name']:
            terms.append('collate ' + column_data['collation_name'])

        if column_data['column_key'] == 'UNI':
            terms.append('unique')

        if column_data['column_default']:
            terms.append('default '
                         + ('current_timestamp'
                                if column_data['column_default'] ==
                                   'current_timestamp'
                                else "'" + column_data['column_default'] + "'"))

        if column_data['is_nullable'] == 'NO':
            terms.append('not null')

        return terms


    def get_column_uniqueness_to_drop(self):
        return self.__column_uniqueness_to_drop


    def get_columns_to_create(self):
        return self.__columns_to_create


    def get_columns_to_drop(self):
        return self.__columns_to_drop


    def get_columns_to_modify(self):
        return self.__columns_to_modify


    def get_foreign_keys_to_create(self):
        return self.__foreign_keys_to_create


    def get_foreign_keys_to_drop(self):
        return self.__foreign_keys_to_drop


    def get_indexes_to_create(self):
        return self.__indexes_to_create


    def get_indexes_to_drop(self):
        return self.__indexes_to_drop


    def get_ref_data_to_add(self):
        return self.__ref_data_to_add


    def get_ref_data_to_modify(self):
        return self.__ref_data_to_modify


    def get_ref_data_to_remove(self):
        return self.__ref_data_to_remove


    def get_ref_tables_to_create(self):
        return self.__ref_tables_to_create


    def get_ref_tables_to_drop(self):
        return self.__ref_tables_to_drop


    def get_tables_to_create(self):
        return self.__tables_to_create


    def get_tables_to_drop(self):
        return self.__tables_to_drop


    def get_unique_keys_to_create(self):
        return self.__unique_keys_to_create


    def get_unique_keys_to_drop(self):
        return self.__unique_keys_to_drop


    def __ksort(self, data):
        results = {}
        for key in sorted(data.keys()):
            results[key] = data[key]

        return results


    def __notice(self, message, indent=None):
        if not self.__cli:
            return

        self.__cli.notice(message, indent)


    def __perform_index_check(self):
        self.__notice('Performing index check...')

        try:
            index_check = ConfigManager.value('index check')
        except:
            self.__notice('not enabled; skipping', 1)
            return False

        if not os.path.isfile(index_check['path']):
            raise RuntimeError(
                'could not find script at "{}"'
                    .format(index_check['path'])
            )

        output = \
            subprocess.check_output(
                [index_check['path'],
                '--server={}'.format(index_check['server']),
                index_check['database']]
            )
        self.__index_usage_parser = \
            MySQLIndexUsageParser() \
                .execute(output)

        if len(self.__index_usage_parser.clustered_indexes) > 0:
            self.__notice('clustered indexes', 1)
            for entry in self.__index_usage_parser.clustered_indexes:
                self.__notice(
                    '(~) {}'
                        .format(
                            entryi[0][:63] + '..'
                                if len(entry[0]) >= 66 else
                            entry[0]
                        ),
                    2
                )

        if len(self.__index_usage_parser.redundant_indexes) > 0:
            self.__notice('redundant indexes', 1)
            for entry in self.__index_usage_parser.redundant_indexes:
                self.__notice(
                    '(!) {}'
                        .format(
                            entryi[0][:63] + '..'
                                if len(entry[0]) >= 66 else
                            entry[0]
                        ),
                    2
                )


    def __process_fks(self, data=tuple()):
        if not data:
            return {}

        fks = {}
        for fk in data:
            if fk['constraint_name'] not in fks.keys():
                fks[fk['constraint_name']] = {
                    'name': fk['constraint_name'],
                    'table_name': fk['table_name'],
                    'ref_table_name': fk['referenced_table_name'],
                    'cols': {},
                    'ref_cols': {},
                    'delete_rule': fk['delete_rule']
                }

            fks[fk['constraint_name']] \
               ['cols'] \
               [int(fk['ordinal_position'])] = \
                fk['column_name']
            fks[fk['constraint_name']] \
               ['ref_cols'] \
               [int(fk['ordinal_position'])] = \
                fk['referenced_column_name']

        for constraint_name, fk in fks.items():
            fks[constraint_name]['cols'] = \
                self.__ksort(fks[constraint_name]['cols'])
            fks[constraint_name]['ref_cols'] = \
                self.__ksort(fks[constraint_name]['ref_cols'])

        return fks


    def __process_uks(self, data=tuple()):
        uks = {}
        for uk in data:
            if uk['constraint_name'] not in uks.keys():
                uks[uk['constraint_name']] = {
                    'name': uk['constraint_name'],
                    'table_name': uk['table_name'],
                    'cols': {}
                }

            uks[uk['constraint_name']] \
               ['cols'] \
               [int(uk['ordinal_position'])] = \
                uk['column_name']

        for name, uk in uks.items():
            uks[name]['cols'] = self.__ksort(uks[name]['cols'])

        return uks


    def __query_source(self, query, binds=tuple()):
        return self.__source.query(query, binds)


    def __query_target(self, query, binds=tuple()):
        return self.__target.query(query, binds)


    def set_cli(self, cli):
        self.__cli = cli
        return self


    def there_are_differences(self):
        return self.__ref_tables_to_create or \
               self.__ref_tables_to_drop or \
               self.__tables_to_create or \
               self.__tables_to_drop or \
               self.__columns_to_create or \
               self.__columns_to_drop or \
               self.__columns_to_modify or \
               self.__column_uniqueness_to_drop or \
               self.__foreign_keys_to_create or \
               self.__foreign_keys_to_drop or \
               self.__ref_data_to_add or \
               self.__ref_data_to_remove or \
               self.__ref_data_to_modify or \
               self.__indexes_to_create or \
               self.__indexes_to_drop or \
               self.__unique_keys_to_create or \
               self.__unique_keys_to_drop


    def __verify_schemas(self):
        self.__notice('Verifying schemas...')

        query = \
            '''select 1 as schema_exists
                 from schemata
                where schema_name = %s'''

        record = self.__source.query(query, [self.__source_db_name])
        if not record:
            self.__error('source schema "'
                         + self.__source_db_name
                         + '" does not exist',
                         1)
            exit(1)

        record = self.__target.query(query, [self.__target_db_name])
        if not record:
            self.__error('target schema "'
                         + self.__target_db_name
                         + '" does not exist',
                         1)
            exit(1)


    def __write_add_foreign_key_constraint_sql(self):
        file_name = '55-foreign_keys.sql'

        self.__notice(file_name, 1)

        contents = ''
        for fk in self.__foreign_keys_to_create:
            contents += \
                ('alter table ' + fk['table_name'] + '\n'
              +  '        add constraint ' + fk['name'] + '\n'
              +  '    foreign key (' + ', '.join(fk['cols'].values()) + ')\n'
              +  ' references ' + fk['ref_table_name'] + '\n'
              +  '            (' + ', '.join(fk['ref_cols'].values()) + ')\n'
              +  '  on delete ' + fk['delete_rule'].lower() + ';\n\n')

        self.__write_file(file_name, contents)


    def __write_add_indexes_sql(self):
        file_name = '65-indexes.sql'

        self.__notice(file_name, 1)

        contents = ''
        for index in self.__indexes_to_create:
            contents += 'create index ' + index['index_name'] + '\n' \
                      + '          on ' + index['table_name'] + '\n' \
                      + '             (' + ', '.join(index['cols']) + ');\n\n'

        self.__write_file(file_name, contents)


    def __write_add_modify_columns_sql(self):
        file_name = '35-columns.sql'

        self.__notice(file_name, 1)

        contents = ''
        for name in self.__columns_to_create:
            table_name, column_name = name.split('.')

            column = self.__source.query(
                '''select table_name,
                          column_name,
                          column_default,
                          is_nullable,
                          character_set_name,
                          collation_name,
                          column_type,
                          column_key,
                          extra
                     from information_schema.columns
                    where table_name = %s
                      and column_name = %s''',
                [table_name, column_name])

            contents += 'alter table ' + column[0]['table_name'] + "\n" \
                      + '        add ' + column[0]['column_name'] + "\n" \
                      + '            ' + column[0]['column_type']

            terms = self.__get_column_terms(column[0])
            if terms:
                contents += "\n"

            for index in range(len(terms)):
                terms[index] = "            " + terms[index]
            contents += "\n".join(terms) + ";\n\n"

        for column in self.__columns_to_modify.values():
            contents += 'alter table ' + column['table_name'] + "\n" \
                      + '     modify ' + column['column_name'] + "\n" \
                      + '            ' + column['column_type']

            terms = self.__get_column_terms(column)
            if terms:
                contents += "\n"

            for index in range(len(terms)):
                terms[index] = "            " + terms[index]
            contents += "\n".join(terms) + ";\n\n"

        for column in self.__columns_to_drop:
            table_name, column_name = column.split('.')

            contents += 'alter table ' + table_name + "\n" \
                      + '       drop ' + column_name + ";\n\n"

        for column in self.__column_uniqueness_to_drop:
            table_name, column_name = column.split('.')

            index = self.__target.query(
                '''show index
                   from ''' + self.__target_db_name + "." + table_name + '''
                   where column_name = %s''',
                [column_name])

            contents += 'alter table ' + index[0]['Table'] + "\n" \
                      + '       drop index ' + index[0]['Key_name'] + ";\n\n"

        self.__write_file(file_name, contents)


    def __write_add_ref_tables_sql(self):
        file_name = '10-ref_tables.sql'

        self.__notice(file_name, 1)

        contents = ''
        for name in self.__ref_tables_to_create:
            record = self.__source.query(
                'show create table ' + self.__source_db_name + '.' + name)
            contents += record[0]['Create Table'] + ";\n\n"

        if contents:
            contents += "\n"

        self.__write_file(file_name, contents)


    def __write_add_tables_sql(self):
        file_name = '30-tables.sql'

        self.__notice(file_name, 1)

        contents = ''
        for name in self.__tables_to_create:
            record = self.__source.query(
                'show create table ' + self.__source_db_name + '.' + name)

            contents += record[0]['Create Table'] + ";\n\n\n"

        self.__write_file(file_name, contents)


    def __write_add_unique_key_constraint_sql(self):
        file_name = '60-unique_keys.sql'

        self.__notice(file_name, 1)

        contents = ''
        for uk in self.__unique_keys_to_create:
            contents += \
                'alter table ' + uk['table_name'] + '\n' \
              + '        add unique key ' + uk['name'] + '\n' \
              + '            (' + ', '.join(uk['cols'].values()) + ');\n\n'

        self.__write_file(file_name, contents)


    def __write_drop_foreign_key_constraint_sql(self):
        file_name = '15-foreign_keys.sql'

        self.__notice(file_name, 1)

        contents = ''
        for fk in self.__foreign_keys_to_drop:
            contents += 'alter table ' + fk['table_name'] + "\n" \
                      + '       drop foreign key ' + fk['name'] + ';\n\n'

        self.__write_file(file_name, contents)


    def __write_drop_indexes_sql(self):
        file_name = '25-indexes.sql'

        self.__notice(file_name, 1)

        contents = ''
        for index in self.__indexes_to_drop:
            contents += 'alter table ' + index['table_name'] + "\n" \
                      + '       drop index ' + index['index_name'] + ";\n\n"

        self.__write_file(file_name, contents)


    def __write_drop_ref_tables_sql(self):
        file_name = '45-ref_tables.sql'

        self.__notice(file_name, 1)

        contents = ''
        for name in self.__ref_tables_to_drop:
            contents += 'drop table if exists ' + name + ';\n\n'

        self.__write_file(file_name, contents)


    def __write_drop_tables_sql(self):
        file_name = '40-tables.sql'

        self.__notice(file_name, 1)

        contents = ''
        for name in self.__tables_to_drop:
            contents += 'drop table if exists ' + name + ';\n\n'

        self.__write_file(file_name, contents)


    def __write_drop_unique_key_constraint_sql(self):
        file_name = '20-unique_keys.sql'

        self.__notice(file_name, 1)

        contents = ''
        for uk in self.__unique_keys_to_drop:
            contents += 'alter table ' + uk['table_name'] + "\n" \
                      + '       drop key ' + uk['name'] + ";\n\n"

        self.__write_file(file_name, contents)


    def __write_ref_table_data_sql(self):
        file_name = '50-ref_data.sql'

        self.__notice(file_name, 1)

        contents = ''
        for data in self.__ref_data_to_add:
            contents += ('insert into ' + data[0] + "\n"
                      +  '(\n'
                      +  '    id,\n'
                      +  '    value,\n'
                      +  '    display_order\n'
                      +  ')\n'
                      +  'values\n'
                      +  '(\n'
                      +  '    ' + str(data[1]) + ',\n'
                      +  "    '" + re.sub("'", "''", data[2]) + "',\n"
                      +  '    ' + str(data[3]) + '\n'
                      +  ');\n'
                      +  'commit;\n\n')

        for data in self.__ref_data_to_modify:
            contents += ('update ' + data[0] + '\n'
                      +  "   set value = '" + data[2] + "',\n"
                      +  "       display_order = " + str(data[3]) + "\n"
                      +  " where id = " + str(data[1]) + ";\n"
                      +  "commit;\n\n")

        for data in self.__ref_data_to_remove:
            contents += 'delete from ' + data[0] + '\n' \
                      + '      where id = ' + str(data[1]) + ';\n' \
                      + 'commit;\n\n'

        self.__write_file(file_name, contents)


    def __write_file(self, file_name, contents):
        f = open(file_name, 'w')
        f.write(contents)
        f.close()


    def __write_upgrade_scripts(self):
        if not self.__enable_write_upgrade_scripts:
            return

        self.__notice('Writing upgrade scripts into current directory...')

        self.__write_add_ref_tables_sql()
        self.__write_drop_foreign_key_constraint_sql()
        self.__write_drop_unique_key_constraint_sql()
        self.__write_drop_indexes_sql()
        self.__write_add_tables_sql()
        self.__write_add_modify_columns_sql()
        self.__write_drop_tables_sql()
        self.__write_drop_ref_tables_sql()
        self.__write_ref_table_data_sql()
        self.__write_add_foreign_key_constraint_sql()
        self.__write_add_unique_key_constraint_sql()
        self.__write_add_indexes_sql()
