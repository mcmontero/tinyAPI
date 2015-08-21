# ----- Info ------------------------------------------------------------------

__author__ = 'Michael Montero <mcmontero@gmail.com>'

# ----- Imports ---------------------------------------------------------------

import re
import tinyAPI

__all__ = [
    'ViewFlipper'
]

# ----- Public Classes --------------------------------------------------------

class ViewFlipper(object):
    '''
    Occasionally you may want to perform operations to reload the data in a
    table without interrupting access to the data currently in it.  One way
    to accomplish this is to create two tables and use a view to point to the
    "active" table (the one being read from).  If you can determine the
    inactive one you can reload the data there then "flip" the view so future
    reads come from the recently reloaded table.
    '''

    def __init__(self, view_name):
        self.view_name = view_name
        self.__schema_name = None
        self.__inactive_table_name = None
        self.__active_table_name = None


    def execute(self):
        self.__set_table_names()

        record = tinyAPI.dsh().one(
            """select table_collation
                 from information_schema.tables
                where table_schema = %s
                  and table_name = %s""",
            [self.__schema_name, self.__inactive_table_name])
        if record is None or record['table_collation'] is None:
            raise RuntimeError(
                'could not determine table collation for "{}.{}"'
                    .format(self.__schema_name, self.__inactive_table_name))

        tinyAPI.dsh().query(
            "set collation_connection = '{}'"
                .format(record['table_collation']))

        tinyAPI.dsh().query(
            "create or replace view {}.{} as select * from {}.{}"
                .format(self.__schema_name,
                        self.view_name,
                        self.__schema_name,
                        self.__inactive_table_name))

        tinyAPI.dsh().commit()


    def get_active_table_name(self):
        self.__set_table_names()
        return self.__active_table_name


    def get_inactive_table_name(self):
        self.__set_table_names()
        return self.__inactive_table_name


    def __set_table_names(self):
        if self.__inactive_table_name is not None and \
           self.__active_table_name is not None:
            return

        record = tinyAPI.dsh().one(
            """select view_definition
                 from information_schema.views
                where table_name = %s""",
            [self.view_name])
        if not record:
            raise RuntimeError(
                'could not retrieve view definition for "'
                + self.view_name
                + '"')

        matches = \
            re.match(
                'select `(.*?)`.`(.*?)`\.',
                record['view_definition'])
        if not matches:
            raise RuntimeError(
                'cannot determine active table from view defintion for "'
                + select.view_name
                + '"')

        self.__schema_name = matches.group(1)

        if matches.group(2) == self.view_name + '_1':
            self.__active_table_name = self.view_name + '_1'
            self.__inactive_table_name = self.view_name + '_2'
        else:
            self.__active_table_name = self.view_name + '_2'
            self.__inactive_table_name = self.view_name + '_1'
