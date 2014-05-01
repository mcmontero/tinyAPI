# ----- Info ------------------------------------------------------------------

__author__ = 'Michael Montero <mcmontero@gmail.com>'

# ----- Imports ---------------------------------------------------------------

from tinyAPI.base.exception import tinyAPIException

__all__ = [
    'SchemaDifferException'
]

# ----- Public Classes --------------------------------------------------------

class SchemaDifferException(tinyAPIException):
    '''Named exception when issues with the Schema Differ arise.'''
    pass
