# ----- Info ------------------------------------------------------------------

__author__ = 'Michael Montero <mcmontero@gmail.com>'

# ----- Imports ---------------------------------------------------------------

__all__ = [
    'ConfigurationException',
    'ContextException',
    'tinyAPIException'
]

# ----- Public Classes --------------------------------------------------------

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


class ContextException(tinyAPIException):
    '''Named exception when issues with context arise.'''
    pass
