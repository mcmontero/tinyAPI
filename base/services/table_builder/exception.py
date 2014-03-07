'''exception.py -- Defines named exceptions for the Table Builder.'''

__author__ = 'Michael Montero <mcmontero@gmail.com>'

# ----- Public Classes -------------------------------------------------------

class TableBuilderException(Exception):
    '''Named exception when issues with the Table Builder arise.'''

    def __init__(self, message):
        self.message = message

    def __str__(self):
        return repr(self.message)

    def get_message(self):
        return self.message;

__all__ = ['TableBuilderException']
