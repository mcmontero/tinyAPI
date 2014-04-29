# ----- Info ------------------------------------------------------------------

__author__ = 'Michael Montero <mcmontero@gmail.com>'

# ----- Imports ---------------------------------------------------------------

from tinyAPI.base.exception import tinyAPIException

__all__ = [
    'TableBuilderException'
]

# ----- Public Classes --------------------------------------------------------

class TableBuilderException(tinyAPIException):
    '''Named exception when issues with the Table Builder arise.'''
    pass
