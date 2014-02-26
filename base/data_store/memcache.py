'''memcache.py -- Abstracts interactions with Memcached for tinyAPI.'''

__author__ = 'Michael Montero <mcmontero@gmail.com>'

# ----- Imports --------------------------------------------------------------

from tinyAPI.base.config import ConfigManager
from tinyAPI.base.singleton import Singleton
import memcache

# ----- Public Classes -------------------------------------------------------

class Memcache(metaclass=Singleton):
    '''Manages interactions with configured Memcached servers.'''

    __handle = None

    def __init__(self):
        self.__handle=memcache.Client(ConfigManager.value('memcached servers'),
                                      debug=0)

    '''Removes the value stored at the specified key from the cache. '''
    def purge(self, key):
        self.__handle.delete(key)

    '''Retrieves the data stored at the specified key from the cache.'''
    def retrieve(self, key):
        value = self.__handle.get(key)
        return value if value else None

    '''Stores the data at the specified key in the cache.'''
    def store(self, key, data, ttl=0):
        self.__handle.set(key, data, ttl)

__all__ = ['Memcache']
