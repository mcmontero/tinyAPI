'''exception.py -- Defines named exceptions for configuration management.'''

__author__ = 'Michael Montero <mcmontero@gmail.com>'

# ----- Public Classes -------------------------------------------------------

class tinyAPIException(Exception):
    '''Base exception for tinyAPI to represent messages in a standard format.'''

    def __init__(self, message):
        self.message = message

    def get_message(self):
        return self.message

    def __str__(self):
        return ("\n====================================================="
                + "======================\n"
                + self.message
                + "\n===================================================="
                + "=======================\n")


class ConfigurationException(tinyAPIException):
    '''Named exception when issues with configuration arise.'''
    pass

__all__ = ['ConfigurationException', 'tinyAPIException']
