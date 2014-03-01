'''mysql.py -- MySQL specific functionality for enhancing data stores.'''

__author__ = 'Michael Montero <mcmontero@gmail.com>'

# ----- Imports --------------------------------------------------------------

import mysql.connector

# ----- Public Classes -------------------------------------------------------

class MySQLCursorDict(mysql.connector.cursor.MySQLCursor):
    '''Defines a MySQL cursor that returns result sets as dictionaries.'''

    def _row_to_python(self, rowdata, desc=None):
            row = super(MySQLCursorDict, self)._row_to_python(rowdata, desc)
            if row:
                return dict(zip(self.column_names, row))
            else:
                return None

__all__ = ['MySQLCursorDict']
