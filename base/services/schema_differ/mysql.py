# ----- Info ------------------------------------------------------------------

__author__ = 'Michael Montero <mcmontero@gmail.com>'

# ----- Imports ---------------------------------------------------------------

from tinyAPI.base.data_store.provider import DataStoreMySQL

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
        self.__write_upgrade_scripts = None
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

        self.__source = DataStoreMySQL()
        self.__source.select_db(source_connection_name, 'information_schema')
        self.__source_db_name = source_db_name

        self.__target = DataStoreMySQL()
        self.__target.select_db(target_connection_name, 'information_schema')
        self.__target_db_name = target_db_name

        self.__write_upgrade_scripts = True


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
                  and table_name not like '%\_ref\_%'"""
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

            for key, value in data.items():
                remove_uniqueness = False

                if key == 'column_key' and \
                   value != 'UNI' and \
                   target[name][key] == 'UNI':
                    # This is special case handling when the unique key is
                    # being removed from a column.  MySQL requires you to drop
                    # the underlying unique index as opposed to modifying the
                    # uniqueness off of the table.
                    self.__notice('(-) ' + name + ' (uniqueness)', 1)

                    self.__column_uniqueness_to_drop.append(name)
                    remove_uniqueness = True

                if target[name][key] != value:
                    if key == 'column_key' and remove_uniqueness:
                        # We've handled this above in the special case for
                        # removing uniqueness.  See the comments there.  There
                        # is nothing to do here since the necessary changes
                        # were recorded above.
                        pass
                    else:
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
                  and k.constraint_name = k.constraint_name
                where k.constraint_schema = %s
                  and k.constraint_name like '%\_fk'"""
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
                  and index_name like '%\_idx'"""
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


    def __compute_ref_table_data_differences(self):
        self.__notice('Computing reference table data differences...')

        query = \
            """select table_name
                 from tables
                where table_schema = %s
                  and table_name like '%\_ref\_%'"""
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
            records = self.__query_source(
                '''select id,
                          value,
                          display_order
                     from ''' + self.__source_db_name + '.' + table + '''
                    order by id asc''')

            source_data[table] = {}

            for record in records:
                source_data[table][record['id']] = [
                    str(record['value']),
                    str(record['display_order'])
                ]

        target_data = {}
        for table in target_tables:
            records = self.__query_target(
                '''select id,
                          value,
                          display_order
                     from ''' + self.__target_db_name + '.' + table + '''
                    order by id asc''')

            target_data[table] = {}

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
                    self.__notice('(-) ' + table + '#' + id, 1)

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
                  and table_name like '%\_ref\_%'"""

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
                  and table_name not like '%\_ref\_%'"""

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


    def dont_write_upgrade_scripts(self):
        self.__write_upgrade_scripts = False
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

        self.__target.close()
        self.__source.close()


    def __flatten_tables(self, tables=tuple()):
        if not tables:
            return []

        results = []
        for table in tables:
            results.append(table['table_name'])

        return results


    def __ksort(self, data):
        results = {}
        for key in sorted(data.keys()):
            results[key] = data[key]

        return results

    def __notice(self, message, indent=None):
        if not self.__cli:
            return

        self.__cli.notice(message, indent)


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


    def __query_source(self, query, binds=tuple()):
        return self.__source.query(query, binds)


    def __query_target(self, query, binds=tuple()):
        return self.__target.query(query, binds)


    def set_cli(self, cli):
        self.__cli = cli
        return self


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
