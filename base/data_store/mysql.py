'''mysql.py -- Abstracts interactions with MySQL for tinyAPI.'''

__author__ = 'Michael Montero <mcmontero@gmail.com>'

# ----- Public Classes -------------------------------------------------------

class DataStoreMySQL(object):
    '''Manages interactions with configured MySQL servers.'''

    __mysql = None

__all__ = ['DataStoreMySQL']
