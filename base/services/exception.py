'''exception.py -- Defines named exceptions for services.'''

__author__ = 'Michael Montero <mcmontero@gmail.com>'

# ----- Public Classes -------------------------------------------------------

class CLIException(Exception):
    '''Named exception when issues with CLI arise.'''

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)

__all__ = ['CLIException']
