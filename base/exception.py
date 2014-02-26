'''exception.py -- Defines named exceptions for configuration management.'''

__author__ = 'Michael Montero <mcmontero@gmail.com>'

# ----- Public Classes -------------------------------------------------------

class ConfigurationException(Exception):
    '''Named exception when issues with configuration arise.'''

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)

__all__ = ['ConfigurationException']
