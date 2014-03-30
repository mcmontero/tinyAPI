# ----- Info ------------------------------------------------------------------

__author__ = 'Michael Montero <mcmontero@gmail.com>'

# ----- Imports ---------------------------------------------------------------

from tinyAPI.base.exception import tinyAPIException

__all__ = [
    'RDBMSBuilderException'
]

# ----- Public Classes --------------------------------------------------------

class RDBMSBuilderException(tinyAPIException):
    '''Named exception when issues with CLI arise.'''
    pass
