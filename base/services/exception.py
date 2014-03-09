'''exception.py -- Defines named exceptions for services.'''

__author__ = 'Michael Montero <mcmontero@gmail.com>'

# ----- Imports --------------------------------------------------------------

from tinyAPI.base.exception import tinyAPIException

# ----- Public Classes -------------------------------------------------------

class CLIException(tinyAPIException):
    '''Named exception when issues with CLI arise.'''
    pass


class DataArmorException(tinyAPIException):
    '''Named exception when issues with Data Armor arise.'''
    pass

__all__ = ['CLIException', 'DataArmorException']
