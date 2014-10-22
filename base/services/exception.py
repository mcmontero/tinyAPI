# ----- Info ------------------------------------------------------------------

__author__ = 'Michael Montero <mcmontero@gmail.com>'

# ----- Imports ---------------------------------------------------------------

from tinyAPI.base.exception import tinyAPIException

__all__ = [
    'CLIException',
    'CryptoException'
]

# ----- Public Classes --------------------------------------------------------

class CLIException(tinyAPIException):
    '''Named exception when issues with CLI arise.'''
    pass


class CryptoException(tinyAPIException):
    '''Named exception when issues with cryptography arise.'''
    pass


class SerializerException(tinyAPIException):
    '''Named exception when issues with the data serializer arise.'''
    pass
