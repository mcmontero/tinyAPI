# ----- Info ------------------------------------------------------------------

__author__ = 'Michael Montero <mcmontero@gmail.com>'

# ----- Imports ---------------------------------------------------------------

from tinyAPI.base.config import ConfigManager
from tinyAPI.base.stats_logger import StatsLogger

import memcache
import threading

__all__ = [
    'Memcache'
]

# ----- Thread Local Data -----------------------------------------------------

_thread_local_data = threading.local()
_thread_local_data.stats = {
    'requests': 0,
    'hits': 0
}
_thread_local_data.cache = {}

# ----- Public Classes --------------------------------------------------------

class Memcache(object):
    '''Manages interactions with configured Memcached servers.'''

    def __init__(self):
        self.__handle = None


    def close(self):
        '''Closes all connections to Memcached servers.'''
        if self.__handle is not None:
            self.__handle.disconnect_all()
            self.__handle = None


    def __connect(self):
        if self.__handle is None:
            self.__handle = \
                memcache.Client(
                    ConfigManager.value('memcached servers'), debug=0)


    def purge(self, key):
        '''Removes the value stored at the specified key from the cache. '''
        self.__connect()

        self.__handle.delete(key)
        if key in _thread_local_data.cache:
            del _thread_local_data.cache[key]


    def retrieve(self, key):
        '''Retrieves the data stored at the specified key from the cache.'''
        StatsLogger().hit_ratio(
            'Cache Stats',
            _thread_local_data.stats['requests'],
            _thread_local_data.stats['hits'])

        _thread_local_data.stats['requests'] += 1

        if key in _thread_local_data.cache:
            _thread_local_data.stats['hits'] += 1
            return _thread_local_data.cache[key].copy()

        self.__connect()

        value = self.__handle.get(key)
        _thread_local_data.cache[key] = value

        return value.copy() if value else None


    def retrieve_multi(self, keys):
        '''Retrieves the data stored for a number of keys from the cache.'''
        StatsLogger().hit_ratio(
            'Cache Stats',
            _thread_local_data.stats['requests'],
            _thread_local_data.stats['hits'])

        _thread_local_data.stats['requests'] += 1

        if key in _thread_local_data.cache:
            _thread_local_data.stats['hits'] += 1
            return _thread_local_data.cache[key].copy()

        self.__connect()

        values = self.__handle.get_multi(keys)
        _thread_local_data.cache[key] = values

        return values.copy() if values else {}


    def store(self, key, data, ttl=0):
        '''Stores the data at the specified key in the cache.'''
        self.__connect()

        self.__handle.set(key, data, ttl)
        _thread_local_data.cache[key] = data
