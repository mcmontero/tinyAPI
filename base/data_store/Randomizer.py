# ----- Info ------------------------------------------------------------------

__author__ = 'Michael Montero <mcmontero@gmail.com>'

# ----- Imports ---------------------------------------------------------------

from .exception import DataStoreException

import copy
import random

# ----- Public Classes --------------------------------------------------------

class Randomizer(object):
    '''
    Implements the randomizer durability algorithm.
    '''

    def __init__(self, settings):
        self.__selected_host = None
        self.settings = copy.deepcopy(settings)

    def next(self):
        if self.__selected_host is not None:
            del self.settings[self.__selected_host]

        if len(self.settings) == 0:
            raise DataStoreException('no more hosts remain')

        if len(self.settings) == 1:
            self.__selected_host = 0
        else:
            self.__selected_host = random.randint(0, len(self.settings) - 1)

        return self.settings[self.__selected_host]
