# ----- Info ------------------------------------------------------------------

__author__ = 'Michael Montero <mcmontero@gmail.com>'

# ----- Imports ---------------------------------------------------------------

from tinyAPI.base.config import ConfigManager

import memcache

__all__ = [
    'Memcache'
]

# ----- Public Classes --------------------------------------------------------

class Memcache(object):
    '''Manages interactions with configured Memcached servers.'''

    def __init__(self):
        self.__handle = \
            memcache.Client(
                ConfigManager.value('memcached servers'), debug=0)


    def purge(self, key):
        '''Removes the value stored at the specified key from the cache. '''
        self.__handle.delete(key)


    def retrieve(self, key):
        '''Retrieves the data stored at the specified key from the cache.'''
        value = self.__handle.get(key)
        return value if value else None


    def store(key, data, ttl=0):
        '''Stores the data at the specified key in the cache.'''
        Memcache().__handle.set(key, data, ttl)
