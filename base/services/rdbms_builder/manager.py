'''manager.py -- Manages building RDBMS schemas based on Table Builder build
   files.'''

__author__ = 'Michael Montero <mcmontero@gmail.com>'

# ----- Import ---------------------------------------------------------------

from .exception import RDBMSBuilderException
from tinyAPI.base.config import ConfigManager
import os
import re
import tinyAPI

# ----- Public Classes -------------------------------------------------------

class Manager(object):
    '''Determines which database objects to build and builds them.'''

    def __init__(self, cli=None):
        self.__cli = cli
        self.__managed_schema = None
        self.__modules = []
        self.__num_rdbms_objects = 0
        self.__num_rdbms_tables = 0
        self.__num_rdbms_indexes = 0
        self.__num_rdbms_routines = 0
        self.__connection_name = None
        self.__dependencies_map = []
        self.__dependents_map = []
        self.__modules_to_build = []
        self.__modules_to_build_prefix = []
        self.__foreign_keys = []
        self.__unindexed_foreign_keys = []

    def __clean_up_rdbms_builder_files(self):
        self.__notice('Cleaning up RDBMS Builder files...');

        for file in os.listdir('/tmp'):
            if re.match('tiny-api-rdbms-builder-', file):
                os.remove(file)
                self.__notice('(-) ' + file, 1)

    def __data_store_not_supported(self):
        raise RDBMSBuilderException(
            'the RDBMS Builder does not currently support "'
            + ConfigManager.value('data_store')
            + '"')

    def __determine_managed_schemas(self):
        self.__notice('Determining managed schemas...')

        schemas = []
        for schema in ConfigManager.value('rdbms builder schemas'):
            schemas.append(schema)

        self.__managed_schemas = ', '.join(schemas)

        self.__notice(self.__managed_schemas, 1)

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

    def __notice(self, message, indent=None):
        if self.__cli is None:
            return None

        self.__cli.notice(message, indent)

    def set_connection_name(self, connection_name):
        '''Tell the RDBMS Builder which connection (configured in
           tinyAPI_config.py) to use for finding and building data
           structures.'''
        self.__connection_name = connection_name
        return self

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
    file varchar(100) not null primary key
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

__all__ = ['Manager']
