# ----- Info ------------------------------------------------------------------

__author__ = 'Michael Montero <mcmontero@gmail.com>'

# ----- Imports ---------------------------------------------------------------

from .exception import DataStoreException

# ----- Public Classes --------------------------------------------------------

class FallBack(object):
    '''
    Implements the fall back durability algorithm.
    '''

    def __init__(self, settings):
        self.__selected_host = None

        if len(settings) != 2:
            raise DataStoreException('exactly 2 hosts must be configured')

        self.settings = settings

    def next(self):
        if self.__selected_host is None:
            self.__selected_host = 0
        elif self.__selected_host == 0:
            self.__selected_host = 1
        else:
            raise DataStoreException('no more hosts remain')

        return self.settings[self.__selected_host]
