'''exception.py -- Defines named exceptions for the Table Builder.'''

__author__ = 'Michael Montero <mcmontero@gmail.com>'

# ----- Public Classes -------------------------------------------------------

class TableBuilderException(Exception):
    '''Named exception when issues with the Table Builder arise.'''

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)

__all__ = ['TableBuilderException']
