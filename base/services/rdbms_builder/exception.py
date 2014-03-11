'''exception.py -- Defines named exceptions for RDBMS Builder.'''

__author__ = 'Michael Montero <mcmontero@gmail.com>'

# ----- Imports ---------------------------------------------------------------

from tinyAPI.base.exception import tinyAPIException

# ----- Public Classes --------------------------------------------------------

class RDBMSBuilderException(tinyAPIException):
    '''Named exception when issues with CLI arise.'''
    pass

__all__ = ['RDBMSBuilderException']
