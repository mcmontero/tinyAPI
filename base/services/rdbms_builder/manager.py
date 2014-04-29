# ----- Info ------------------------------------------------------------------

__author__ = 'Michael Montero <mcmontero@gmail.com>'

# ----- Imports ---------------------------------------------------------------

from .exception import RDBMSBuilderException
from tinyAPI.base.config import ConfigManager
from tinyAPI.base.data_store.exception import DataStoreDuplicateKeyException
from tinyAPI.base.utils import find_dirs, find_files

import hashlib
import importlib.machinery
import os
import re
import subprocess
import sys
import tempfile
import tinyAPI

__all__ = [
    'Manager'
]

# ----- Protected Classes -----------------------------------------------------

class _RDBMSBuilderModuleSQL(object):
    '''Simple container for all of the SQL related assets for a module.'''

    def __init__(self, name, prefix):
        self.__name = name
        self.__prefix = prefix
        self.__dml_files = []
        self.__build_file = None
        self.__definitions = []
        self.__indexes = []
        self.__inserts = []


    def add_definition(self, db_name, statement):
        self.__definitions.append([db_name, statement])
        return self


    def add_dml_file(self, dml_file):
        self.__dml_files.append(dml_file)
        return self


    def add_index(self, db_name, statement):
        self.__indexes.append([db_name, statement])
        return self


    def add_insert(self, db_name, statement):
        self.__inserts.append([db_name, statement])
        return self


    def get_build_file(self):
        return self.__build_file


    def get_definitions(self):
        return self.__definitions


    def get_dml_files(self):
        return self.__dml_files


    def get_indexes(self):
        return self.__indexes


    def get_inserts(self):
        return self.__inserts


    def get_name(self):
        return self.__name


    def get_prefix(self):
        return self.__prefix


    def set_build_file(self, build_file):
        self.__build_file = build_file
        return self

# ----- Public Classes --------------------------------------------------------

class Manager(object):
    '''Determines which database objects to build and builds them.'''

    def __init__(self, cli=None):
        self.__cli = cli
        self.__managed_schema = None
        self.__modules = {}
        self.__num_rdbms_objects = 0
        self.__num_rdbms_tables = 0
        self.__num_rdbms_indexes = 0
        self.__num_rdbms_routines = 0
        self.__connection_name = None
        self.__exec_sql_command = None
        self.__dependencies_map = {}
        self.__dependents_map = {}
        self.__modules_to_build = {}
        self.__modules_to_build_prefix = {}
        self.__prefix_to_module = {}
        self.__foreign_keys = {}
        self.__unindexed_foreign_keys = []


    def __add_foreign_key_constraints(self):
        self.__notice("Adding foreign key constraints...")

        for module_name in self.__foreign_keys.keys():
            if module_name in self.__modules_to_build:
                for fk in self.__foreign_keys[module_name]:
                    db_name = fk[0]
                    foreign_key = fk[1]

                    matches = re.search('add constraint (.*?)$',
                                        foreign_key,
                                        re.M | re.I | re.S)
                    if matches is None:
                        raise RDBMSBuilderException(
                                'could not find name of constraint in '
                                + 'statement:\n'
                                + foreign_key)

                    self.__execute_statement(foreign_key, db_name)
                    self.__notice('(+) ' + matches.group(1), 1)

                    self.__num_rdbms_objects += 1


    def __assemble_all_modules(self):
        '''Finds all of the modules in the application and puts their
           respective parts together in a centralize module object.'''
        self.__notice('Assembling all modules...')

        ##
        # Step 1
        #
        # Take an initial pass at building the modules with the minimum set of
        # information required.  This is necessary so that the second pass can
        # properly assign dependencies based on knowing all of the available
        # modules.
        ##

        for path in ConfigManager.value('application dirs'):
            files = find_files(path + '/*', 'build.py')
            for file in files:
                if file != '':
                    module_name = None
                    prefix = None

                    matches = re.search('(.*)/sql/ddl/build.py$', file)
                    if matches is not None:
                        module_name = matches.group(1).split('/')[-1]

                        with open(file) as f:
                            contents = f.read()

                        if contents != '':
                            matches = re.search('def (.*?)_build\s?\(',
                                                contents,
                                                re.M | re.S | re.I)
                            if matches is None:
                                raise RDBMSBuilderException(
                                        'found build.py file but could not '
                                        + 'find build function in "'
                                        + file
                                        + '"')

                            prefix = matches.group(1)

                    if module_name is not None and prefix is not None:
                        module = _RDBMSBuilderModuleSQL(module_name, prefix)
                        module.set_build_file(file)
                        self.__modules[module_name] = module
                        self.__prefix_to_module[prefix] = module_name

                        if module_name not in self.__dependencies_map:
                            self.__dependencies_map[module_name] = []

                        if module_name not in self.__dependents_map:
                            self.__dependents_map[module_name] = []

        ##
        # Step 2
        #
        # Take a second pass at all of the modules, assign dependencies and
        # associate all necessary SQL so the objects can be built.
        ##

        for module in self.__modules.values():
            loader = importlib.machinery.SourceFileLoader(
                        module.get_name(), module.get_build_file())
            build_file = loader.load_module(module.get_name())

            build = getattr(build_file, module.get_prefix() + '_build')
            objects = build()

            for object in objects:
                module.add_definition(object.get_db_name(),
                                      object.get_definition())

                if isinstance(object, tinyAPI.Table):
                    self.__assign_dependencies(module, object)

                indexes = object.get_index_definitions()
                for index in indexes:
                    module.add_index(object.get_db_name(), index)

                inserts = object.get_insert_statements()
                if inserts is not None:
                    for insert in inserts:
                        module.add_insert(object.get_db_name(), insert)

                fks = object.get_foreign_key_definitions()
                for fk in fks:
                    if module.get_name() not in self.__foreign_keys:
                        self.__foreign_keys[module.get_name()] = []

                    self.__foreign_keys[module.get_name()].append([
                            object.get_db_name(), fk + ';'])

                self.__unindexed_foreign_keys = \
                    self.__unindexed_foreign_keys + \
                    object.get_unindexed_foreign_keys()

            self.__handle_module_dml(module, path)


    def __assign_dependencies(self, module, table):
        '''Record all of the dependencies between modules so the system can be
           rebuilt with dependencies in mind.'''
        dependencies = table.get_dependencies()
        for dependency in dependencies:
            if dependency not in self.__prefix_to_module.keys():
                raise RDBMSBuilderException(
                        'found dependency "' + dependency + '" but do not have '
                        + 'a module for it')

            if module.get_name() != self.__prefix_to_module[dependency]:
                self.__dependencies_map[module.get_name()] \
                    .append(self.__prefix_to_module[dependency])

                if self.__prefix_to_module[dependency] not in \
                   self.__dependents_map:
                    self.__dependents_map[
                        self.__prefix_to_module[dependency]] = []

                self.__dependents_map[self.__prefix_to_module[dependency]] \
                                .append(module.get_name())


    def __build_dml(self, module):
        for file in module.get_dml_files():
            with open(file, 'rb') as f:
                self.__execute_statement(f.read())

            self.__track_module_info(module, file)

        routines = tinyAPI.dsh().query(
            """select routine_type,
                      routine_name
                 from information_schema.routines
                where routine_name like '"""
                + module.get_prefix()
                + "\_%'")

        for routine in routines:
            self.__notice('(+) '
                          + routine['routine_type'].lower()
                          + ' '
                          + routine['routine_name'],
                          2)

            self.__num_rdbms_routines += 1


    def __build_sql(self, module):
        statements = module.get_definitions()
        if len(statements) > 0:
            for statement in statements:
                matches = re.search('^create table (.*?)$',
                                    statement[1],
                                    re.M | re.S | re.I)
                if matches is not None:
                    self.__notice('(+) '
                                  + statement[0]
                                  + '.'
                                  + matches.group(1), 2)
                    self.__num_rdbms_tables += 1
                    self.__num_rdbms_objects += 1

                self.__execute_statement(statement[1], statement[0])

        statements = module.get_indexes()
        if len(statements) > 0:
            for statement in statements:
                matches = re.match('create index (.*?)$',
                                   statement[1],
                                   re.M | re.S | re.I)
                if matches is not None:
                    self.__notice('(+) '
                                  + statement[0]
                                  + '.'
                                  + matches.group(1), 2)
                    self.__num_rdbms_indexes += 1
                    self.__num_rdbms_objects += 1

                self.__execute_statement(statement[1], statement[0])

        self.__display_insert_progress(module.get_inserts())
        self.__track_module_info(module, module.get_build_file())


    def __clean_up_rdbms_builder_files(self):
        self.__notice('Cleaning up RDBMS Builder files...');

        for file in os.listdir('/tmp'):
            if re.match('tinyAPI_rdbms_builder_', file):
                os.remove('/tmp/' + file)
                self.__notice('(-) /tmp/' + file, 1)


    def __compile_build_list_by_changes(self):
        '''Mark for build modules that contain modified build or DML files.'''
        for module in list(self.__modules.values()):
            requires_build = False

            if self.__file_has_been_modified(module.get_build_file()):
                requires_build = True
            else:
                for file in module.get_dml_files():
                    if self.__file_has_been_modified(file):
                        requires_build = True
                        break

            if requires_build and \
               module.get_name() not in self.__modules_to_build:
                self.__notice('(+) ' + module.get_name(), 1)
                self.__compile_build_list_for_module(module.get_name())


    def __compile_build_list_for_all_modules(self):
        '''Force a build for all modules.'''
        for module_name in list(self.__modules.keys()):
            self.__compile_build_list_for_module(module_name)


    def __compile_build_list_for_module(self, module_name):
        '''Mark a module for building and determine which of its dependents
           also needs to be build.'''
        self.__modules_to_build[
            module_name] = True;
        self.__modules_to_build_prefix[
            self.__modules[module_name].get_prefix()] = True

        if module_name in self.__dependents_map:
            for dependent in self.__dependents_map[module_name]:
                if dependent not in self.__modules_to_build:
                    self.__compile_build_list_for_module(dependent)


    def __compile_dirty_module_list(self):
        self.__notice('Determining if there are dirty modules...')

        records = tinyAPI.dsh().query(
            '''select name
                 from rdbms_builder.dirty_module''')

        for record in records:
            if record['name'] not in self.__modules:
                # The dirty module is no longer part of the application, so
                # we should stop tracking it here.
                self.__notice('(-) ' + record['name'], 1)

                tinyAPI.dsh().query(
                    '''delete from rdbms_builder.dirty_module
                        where name = %s''',
                    [record['name']])
                tinyAPI.dsh().commit()
            else:
                self.__notice('(+) ' + record['name'], 1)
                self.__compile_build_list_for_module(record['name'])


    def __compile_reference_definitions(self):
        '''Compile the reference tables created with RefTable() into variables
           so that no database interactions are required to interact with
           them.'''
        if ConfigManager.value('reference definition file') is None:
            return

        self.__notice('Compiling reference definitions...')

        if ConfigManager.value('data store') != 'mysql':
            self.__data_store_not_supported()

        reference_tables = tinyAPI.dsh().query(
            """select table_schema,
                      table_name
                 from tables
                where table_schema in (""" + self.__managed_schemas + """)
                  and table_name like '%\_ref\_%'
                order by table_name asc""")

        content = """
# +---------------------------------------------------------------------------+
# | WARNING - MACHINE GENERATED FILE                                          |
# +---------------------------------------------------------------------------+

##
# Any changes that you make directly to this file WILL BE LOST!  It was auto-
# generated by the RDBMS Builder.
##

# ----- Imports ---------------------------------------------------------------

import builtins

# ----- Instructions ----------------------------------------------------------

# TABLE tinyAPI_ref_unit_test
builtins.TINYAPI_UNIT_TEST_ONE = 1
builtins.TINYAPI_UNIT_TEST_TWO = 2
builtins.TINYAPI_UNIT_TEST_THREE = 3
def _tinyapi_ref_unit_test():
    return {
        1: "one",
        2: "two",
        3: "three"
    }
builtins._tinyapi_ref_unit_test = _tinyapi_ref_unit_test

"""
        index = 0
        for reference_table in reference_tables:
            data = tinyAPI.dsh().query(
                """select value,
                          id
                     from """
                          + reference_table['table_schema']
                          + '.'
                          + reference_table['table_name'] + """
                    order by id asc""")

            if index > 0:
                content += "\n"
            index += 1

            content += "# TABLE " + reference_table['table_name'] + "\n"

            values = []
            for item in data:
                value = re.sub('[^A-Za-z0-9_]',
                              '_',
                              reference_table['table_name']
                              + '_'
                              + item['value'])
                value = re.sub('_ref_', '_', value)
                value = re.sub('[_]+', '_', value)

                content += ('builtins.'
                            + value.upper()
                            + ' = '
                            + str(item['id']) + "\n")

                values.append('       '
                              + str(item['id'])
                              + ': "'
                              + item['value']
                              + '"')

            content += ("def _"
                        + reference_table['table_name']
                        + '():\n'
                        + '    return {\n'
                        + ",\n".join(values)
                        + '\n    }\n'
                        + 'builtins._'
                        + reference_table['table_name' ]
                        + ' = _'
                        + reference_table[ 'table_name' ]
                        + "\n")

        f = open(ConfigManager.value('reference definition file'), 'w')
        f.write(content.lstrip())
        f.close()


    def __data_store_not_supported(self):
        raise RDBMSBuilderException(
            'the RDBMS Builder does not currently support "'
            + ConfigManager.value('data store')
            + '"')


    def __determine_managed_schemas(self):
        '''The database may contain many schemas, some of which should be
           ignored by tinyAPI.  A list of which schemas to manage is created
           here.'''
        self.__notice('Determining managed schemas...')

        schemas = []
        for schema in ConfigManager.value('rdbms builder schemas'):
            schemas.append("'" + schema + "'")

        self.__managed_schemas = ', '.join(schemas)

        self.__notice(self.__managed_schemas, 1)


    def __display_insert_progress(self, inserts=tuple()):
        if len(inserts) == 0:
            return

        print('        (+) adding table data ', end = '')
        sys.stdout.flush()

        chars = ['-', '-', '\\', '\\', '|', '|', '/', '/']
        index = 0
        for insert in inserts:
            print(chars[index], end = '')
            sys.stdout.flush()
            self.__execute_statement(insert[1], insert[0])
            print("\b", end = '')
            sys.stdout.flush()

            index += 1
            if index >= len(chars):
                index = 0

        print(" ")


    def __drop_foreign_key_constraints(self):
        self.__notice('Dropping relevant foreign key constraints...')

        if ConfigManager.value('data store') != 'mysql':
            self.__data_store_not_supported()

        constraints = tinyAPI.dsh().query(
            '''select constraint_schema,
                      table_name,
                      constraint_name
                 from referential_constraints
                where constraint_schema in ('''
                      + self.__managed_schemas
                      + ')')

        for constraint in constraints:
            parts = constraint['constraint_name'].split('_')
            if parts[0] in self.__modules_to_build_prefix:
                self.__notice('(-) ' + constraint['constraint_name'], 1)

                tinyAPI.dsh().query(
                    'alter table '
                    + constraint['constraint_schema']
                    + '.'
                    + constraint['table_name']
                    + ' drop foreign key '
                    + constraint['constraint_name'])


    def __drop_objects(self):
        self.__notice('Dropping objects that will be rebuilt...')

        if ConfigManager.value('data store') != 'mysql':
            self.__data_store_not_supported()

        tables = tinyAPI.dsh().query(
            '''select table_schema,
                      table_name
                 from tables
                where table_schema in ('''
                      + self.__managed_schemas
                      + ')')
        for table in tables:
            parts = table['table_name'].split('_')

            if parts[0] in self.__modules_to_build_prefix:
                self.__notice('(-) table ' + table['table_name'], 1)

                tinyAPI.dsh().query(
                    'drop table '
                    + table['table_schema' ]
                    + '.'
                    + table['table_name'])

        routines = tinyAPI.dsh().query(
            '''select routine_schema,
                      routine_type,
                      routine_name
                 from routines
                where routine_schema in ('''
                      + self.__managed_schemas
                      + ')')
        for routine in routines:
            parts = routine['routine_name'].split('_')

            if parts[0] in self.__modules_to_build_prefix:
                self.__notice('(-) '
                              + routine['routine_type'].lower()
                              + ' '
                              + routine['routine_name'])

                tinyAPI.dsh().query(
                    'drop type '
                    + routine['routine_schema']
                    + '.'
                    + routine['routine_name'])


    def __enhance_build_error(self, message):
        if ConfigManager.value('data store') != 'mysql':
            return ''

        if re.match('ERROR (1005|1215)', message) or \
           re.search('errno: 150', message):
            return ('\n\npossible causes:\n\n'
                    + 'o A column that has a foreign key is not the exact '
                    + 'same type as the column it is\n  referencing.\n\n'
                    + 'o The column you are trying to reference does not have '
                    + 'an index on it.\n\n'
                    + 'o The table name provided for the parent table does not '
                    + 'exist.\n')
        else:
            return ''


    def __error(self, message, indent=None):
        if self.__cli is None:
            return None

        self.__cli.error(message, indent)


    def execute(self):
        '''Causes the RDBMS Builder to perform all necessary tasks.'''
        if self.__connection_name is None:
            raise RDBMSBuilderException('connection name has not been set')

        # +------------------------------------------------------------------+
        # | Step 1                                                           |
        # |                                                                  |
        # | Clean up unused RDBMS Builder files.                             |
        # +------------------------------------------------------------------+

        self.__clean_up_rdbms_builder_files()

        # +------------------------------------------------------------------+
        # | Step 2                                                           |
        # |                                                                  |
        # | Verify that the RDBMS Builder database objects exist and if they |
        # | do not, alert with instructions on how to make them.             |
        # +------------------------------------------------------------------+

        self.__verify_rdbms_builder_objects()

        # +------------------------------------------------------------------+
        # | Step 3                                                           |
        # |                                                                  |
        # | Determine which schemas should be managed by the RDBMS Builder.  |
        # +------------------------------------------------------------------+

        self.__determine_managed_schemas()

        # +------------------------------------------------------------------+
        # | Step 4                                                           |
        # |                                                                  |
        # | Execute any SQL files that are intended to be loaded before the  |
        # | the build.                                                       |
        # +------------------------------------------------------------------+

        if self.__cli is not None and self.__cli.args.all is True:
            self.__execute_prebuild_scripts()

        # +------------------------------------------------------------------+
        # | Step 5                                                           |
        # |                                                                  |
        # | Create an array containing data about all modules that exist in  |
        # | this API.                                                        |
        # +------------------------------------------------------------------+

        self.__assemble_all_modules()

        # +------------------------------------------------------------------+
        # | Step 6                                                           |
        # |                                                                  |
        # | If there are modules that have been marked dirty, add them to    |
        # | the build.                                                       |
        # +------------------------------------------------------------------+

        self.__compile_dirty_module_list()

        # +------------------------------------------------------------------+
        # | Step 7                                                           |
        # |                                                                  |
        # | Compile the list of modules that need to be build.               |
        # +------------------------------------------------------------------+

        if self.__cli is not None and self.__cli.args.all is True:
            self.__notice('Compiling build list of all modules...')
            self.__compile_build_list_for_all_modules()
        else:
            if self.__cli.args.module_name is not None:
                self.__notice('Compiling build list for specific module...')
                self.__notice('(+) ' + self.__cli.args.module_name, 1)
                self.__compile_build_list_for_module(
                    self.__cli.args.module_name)
            else:
                self.__notice('Comiling build list based on changes...')
                self.__compile_build_list_by_changes()

        # +------------------------------------------------------------------+
        # | Step 8                                                           |
        # |                                                                  |
        # | Determine if the build should continue.                          |
        # +------------------------------------------------------------------+

        if len(self.__modules_to_build.keys()) == 0:
            self.__notice('RDBMS is up to date!')

            if self.__cli is not None:
                self.__cli.exit()
            else:
                sys.exit(0)

        # +------------------------------------------------------------------+
        # | Step 9                                                           |
        # |                                                                  |
        # | Drop all foreign key constraints for the tables that need to be  |
        # | built so we can tear down objects without errors.                |
        # +------------------------------------------------------------------+

        self.__drop_foreign_key_constraints()

        # +------------------------------------------------------------------+
        # | Step 10                                                          |
        # |                                                                  |
        # | Drop objects for modules marked for rebuild.                     |
        # +------------------------------------------------------------------+

        self.__drop_objects()

        # +------------------------------------------------------------------+
        # | Step 11                                                          |
        # |                                                                  |
        # | Rebuild modules.                                                 |
        # +------------------------------------------------------------------+

        self.__rebuild_modules()

        # +------------------------------------------------------------------+
        # | Step 12                                                          |
        # |                                                                  |
        # | Recompile all DML.                                               |
        # +------------------------------------------------------------------+

        self.__recompile_dml()

        # +------------------------------------------------------------------+
        # | Step 13                                                          |
        # |                                                                  |
        # | Add all foreign key constraints.                                 |
        # +------------------------------------------------------------------+

        self.__add_foreign_key_constraints()

        # +------------------------------------------------------------------+
        # | Step 14                                                          |
        # |                                                                  |
        # | Verify foreign key indexes.                                      |
        # +------------------------------------------------------------------+

        self.__verify_foreign_key_indexes()

        # +------------------------------------------------------------------+
        # | Step 15                                                          |
        # |                                                                  |
        # | Compile reference table data into variables.                     |
        # +------------------------------------------------------------------+

        self.__compile_reference_definitions()

        # +------------------------------------------------------------------+
        # | Step 16                                                          |
        # |                                                                  |
        # | Report interesting stats about the build.                        |
        # +------------------------------------------------------------------+

        self.__notice('RDBMS Builder stats:')
        self.__notice('       # tables: '
                      + '{:,}'.format(self.__num_rdbms_tables),
                      1)
        self.__notice('      # indexes: '
                      + '{:,}'.format(self.__num_rdbms_indexes),
                      1)
        self.__notice('     # routines: '
                      + '{:,}'.format(self.__num_rdbms_routines),
                      1)
        self.__notice('--------------------', 1)
        self.__notice('total # objects: '
                      + '{:,}'.format(self.__num_rdbms_objects),
                      1)


    def __execute_prebuild_scripts(self):
        self.__notice('Finding and executing pre-build files...')

        for path in ConfigManager.value('application dirs'):
            dirs = find_dirs(path + '/*', 'rdbms_prebuild')
            for dir in dirs:
                self.__notice(dir, 1)
                files = os.listdir(dir)
                files.sort()
                for file in files:
                    if re.search('\.sql$', file):
                        self.__notice(file, 2)

                        try:
                            subprocess.check_output(
                                self.__get_exec_sql_command()
                                + ' < ' + dir + '/' + file,
                                stderr=subprocess.STDOUT,
                                shell=True)
                        except subprocess.CalledProcessError as e:
                            raise RDBMSBuilderException(
                                    e.output.rstrip().decode())


    def __execute_statement(self, statement, db_name=None):
        file = tempfile.NamedTemporaryFile(dir='/tmp',
                                           prefix='tinyAPI_rdbms_builder_',
                                           delete=False)

        file.write(statement.encode())
        file.close()

        try:
            subprocess.check_output(
                self.__get_exec_sql_command()
                + ('' if db_name is None else ' --database=' + db_name)
                + ' < ' + file.name,
                stderr=subprocess.STDOUT,
                shell=True)
        except subprocess.CalledProcessError as e:
            message = e.output.rstrip().decode()

            if len(statement) <= 2048:
                raise RDBMSBuilderException(
                        'execution of this:\n\n'
                        + statement
                        + "\n\nproduced this error:\n\n"
                        + message
                        + self.__enhance_build_error(message))
            else:
                raise RDBMSBuilderException(
                        'execution of this file:\n\n'
                        + file.name
                        + "\n\nproduced this error:\n\n"
                        + message
                        + self.__enhance_build_error(message))

        os.remove(file.name)


    def __file_has_been_modified(self, file):
        if ConfigManager.value('data store') != 'mysql':
            self.__data_store_not_supported()

        with open(file, 'rb') as f:
            sha1 = hashlib.sha1(f.read()).hexdigest();

        records = tinyAPI.dsh().query(
            '''select sha1
                 from rdbms_builder.module_info
                where file = %s''',
            [file])

        return len(records) == 0 or records[0]['sha1'] != sha1


    def __get_exec_sql_command(self):
        if self.__exec_sql_command is not None:
            return self.__exec_sql_command

        if ConfigManager.value('data store') == 'mysql':
            if self.__connection_name is None:
                raise RDBMSBuilderException(
                    'cannot execute SQL because connection name has not been '
                    + 'set')

            connection_data = ConfigManager.value('mysql connection data')
            if self.__connection_name not in connection_data:
                raise RDBMSBuilderException(
                    'no connection data has been configured for "'
                    + self.__connection_name
                    + '"')

            host = connection_data[self.__connection_name][0]
            user = connection_data[self.__connection_name][1]
            password = connection_data[self.__connection_name][2]

            command = ['/usr/bin/mysql']
            if host != '':
                command.append('--host=' + host)

            if user != '':
                command.append('--user=' + user)

            if password != '':
                command.append("--password='" + password + "'")

            if user == '' and password == '':
                command.append('--user root')

            self.__exec_sql_command = ' '.join(command)
            return self.__exec_sql_command
        else:
            self.__data_store_not_supported()


    def __handle_module_dml(self, module, path):
        files = find_files(path, "*.sql")
        for file in files:
            if re.search('/rdbms_prebuild/', file) is None:
                module.add_dml_file(file)


    def __notice(self, message, indent=None):
        if self.__cli is None:
            return None

        self.__cli.notice(message, indent)


    def __rebuild_modules(self):
        self.__notice('Rebuilding all DDL...')

        for module_name in self.__modules_to_build.keys():
            self.__notice('building module ' + module_name, 1)
            self.__build_sql(self.__modules[module_name])


    def __recompile_dml(self):
        self.__notice('Recompiling all DML...')

        for module_name in self.__modules_to_build.keys():
            dml_files = self.__modules[module_name].get_dml_files()
            if len(dml_files) > 0:
                self.__notice('compiling for ' + module_name, 1);

                self.__build_dml(self.__modules[module_name])


    def set_connection_name(self, connection_name):
        '''Tell the RDBMS Builder which connection (configured in
           tinyAPI_config.py) to use for finding and building data
           structures.'''
        self.__connection_name = connection_name
        return self


    def __track_module_info(self, module, file):
        if ConfigManager.value('data store') != 'mysql':
            self.__data_store_not_supported()

        with open(file, 'rb') as f:
            sha1 = hashlib.sha1(f.read()).hexdigest();

        tinyAPI.dsh().query(
            '''insert into rdbms_builder.module_info
               (
                  file,
                  sha1
               )
               values
               (
                  %s,
                  %s
               )
               on duplicate key
               update sha1 = %s''',
            [file, sha1, sha1])

        tinyAPI.dsh().query(
            '''delete from rdbms_builder.dirty_module
                where name = %s''',
            [module.get_name()])

        tinyAPI.dsh().commit()


    def __verify_foreign_key_indexes(self):
        self.__notice('Verifying foreign key indexes...')

        for data in self.__unindexed_foreign_keys:
            table_name = data[0]
            parent_table_name = data[1]
            cols = data[2]
            parent_cols = data[3]

            parts = table_name.split('_')

            try:
                tinyAPI.dsh().create(
                    'rdbms_builder.dirty_module',
                    {'name': parts[0]})
                tinyAPI.dsh().commit()
            except DataStoreDuplicateKeyException:
                pass

            self.__notice('(!) unindexed foreign key', 1)
            self.__notice('table: '
                          + table_name
                          + ' -> parent: '
                          + parent_table_name,
                          2)
            self.__notice(repr(cols) + ' -> ' + repr(parent_cols), 2)
            self.__notice('--------------------------------------------------'
                          + '------------', 2)

        if len(self.__unindexed_foreign_keys) > 0:
            raise RDBMSBuilderException('unindexed foreign keys (see above)')


    def __verify_rdbms_builder_objects(self):
        if ConfigManager.value('data store') != 'mysql':
            self.__data_store_not_supported()

        tinyAPI.dsh().select_db(self.__cli.args.connection_name,
                                'information_schema')

        databases = tinyAPI.dsh().query('show databases')
        for database in databases:
            if database['Database'] == 'rdbms_builder':
                return

        build_instructions = '''
create database rdbms_builder;

create table rdbms_builder.module_info
(
    file varchar(100) not null primary key,
    sha1 char(40) not null
);

create table rdbms_builder.dirty_module
(
    name varchar(100) not null primary key
);

grant all privileges
   on rdbms_builder.*
   to ''@'localhost'
      identified by '';

flush privileges;'''

        raise RDBMSBuilderException(
            'RDBMS Builder database and objects do not exist; create them as '
            + 'root using:\n'
            + build_instructions)


    def __warn(self, message, indent=None):
        if self.__cli is None:
            return None

        self.__cli.warn(message, indent)
