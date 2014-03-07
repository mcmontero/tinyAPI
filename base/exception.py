'''exception.py -- Defines named exceptions for configuration management.'''

__author__ = 'Michael Montero <mcmontero@gmail.com>'

# ----- Public Classes -------------------------------------------------------

class ConfigurationException(Exception):
    '''Named exception when issues with configuration arise.'''

    def __init__(self, message):
        self.message = message

    def __str__(self):
        return repr(self.message)

__all__ = ['ConfigurationException']
