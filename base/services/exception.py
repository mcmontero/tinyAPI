'''exception.py -- Defines named exceptions for services.'''

__author__ = 'Michael Montero <mcmontero@gmail.com>'

# ----- Public Classes -------------------------------------------------------

class CLIException(Exception):
    '''Named exception when issues with CLI arise.'''

    def __init__(self, message):
        self.message = message

    def __str__(self):
        return repr(self.message)


class DataArmorException(Exception):
    '''Named exception when issues with Data Armor arise.'''

    def __init__(self, message):
        self.message = message

    def __str__(self):
        return repr(self.message)

__all__ = ['CLIException', 'DataArmorException']
