# ----- Info ------------------------------------------------------------------

__author__ = 'Michael Montero <mcmontero@gmail.com>'

# ----- Imports ---------------------------------------------------------------

from tinyAPI.base.config import ConfigManager
from tinyAPI.base.stats_logger import StatsLogger

import memcache
import threading
import time

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


    def __add_to_local_cache(self, key, data=None, ttl=None):
        if key not in _thread_local_data.cache:
            _thread_local_data.cache[key] = {
                'added': (time.time() if data is not None else None),
                'data': data,
                'ttl': ttl
            }


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


    def __get_from_local_cache(self, key):
        if key not in _thread_local_data.cache or \
           _thread_local_data.cache[key]['data'] is None:
            return None

        added = _thread_local_data.cache[key]['added']
        ttl = _thread_local_data.cache[key]['ttl']
        if added is not None and ttl is not None:
            if time.time() - added >= ttl:
                return None

        return _thread_local_data.cache[key]['data'].copy()


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

        data = self.__get_from_local_cache(key)
        if data is not None:
            _thread_local_data.stats['hits'] += 1
            return data

        self.__connect()

        value = self.__handle.get(key)
        if value is not None:
            self.__add_to_local_cache(key, value)

        return value.copy() if value else None


    def retrieve_multi(self, keys):
        '''Retrieves the data stored for a number of keys from the cache.'''
        StatsLogger().hit_ratio(
            'Cache Stats',
            _thread_local_data.stats['requests'],
            _thread_local_data.stats['hits'])

        _thread_local_data.stats['requests'] += 1

        data = self.__get_from_local_cache(key)
        if data is not None:
            _thread_local_data.stats['hits'] += 1
            return data

        self.__connect()

        values = self.__handle.get_multi(keys)
        if values is not None:
            self.__add_to_local_cache(key, values)

        return values.copy() if values else {}


    def store(self, key, data, ttl=0, local_cache_ttl=None):
        '''Stores the data at the specified key in the cache.'''
        self.__connect()

        self.__handle.set(key, data, ttl)
        self.__add_to_local_cache(key, data, local_cache_ttl)
