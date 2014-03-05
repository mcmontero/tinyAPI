'''config.py -- Manages the retrieval and validation of configuration
   settings.'''

__author__ = 'Michael Montero <mcmontero@gmail.com>'

# ----- Imports ---------------------------------------------------------------

from .exception import ConfigurationException
import tinyAPI_config

# ----- Public Classes --------------------------------------------------------

class ConfigManager(object):
    '''Handles retrieval and validation of configuration settings.'''

    @staticmethod
    def value(key):
        '''Retrieves the configuration value named by key.'''
        if key in tinyAPI_config.values:
            return tinyAPI_config.values[key]
        else:
            raise ConfigurationException(
                '"' + key + '" is not configured in tinyAPI_config')

__all__ = ['ConfigManager']
