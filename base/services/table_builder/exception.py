'''exception.py -- Defines named exceptions for the Table Builder.'''

__author__ = 'Michael Montero <mcmontero@gmail.com>'

# ----- Import ---------------------------------------------------------------

from tinyAPI.base.exception import tinyAPIException

# ----- Public Classes -------------------------------------------------------

class TableBuilderException(tinyAPIException):
    '''Named exception when issues with the Table Builder arise.'''
    pass

__all__ = ['TableBuilderException']
