# ----- Info ------------------------------------------------------------------

__author__ = 'Michael Montero <mcmontero@gmail.com>'

# ----- Import ----------------------------------------------------------------

from .exception import MarshallerException

import re

__all__ = [
    'Marshaller'
]

# ----- Public Classes --------------------------------------------------------

class Marshaller(object):
    '''A generic data marshaller that can convert formatted SQL results into
       their JSON representation.'''

    def __init__(self):
        self.__objects = []
        self.reset()


    def add_object(self, name):
        self.__objects.append(name)
        return self


    def format(self, record):
        self.reset()

        for key, value in record.items():
            matches = re.search('^__(.*?)__(.*?)$', key)
            if not matches:
                self.data[key] = value
            else:
                if matches.group(1) not in self.__objects:
                    raise MarshallerException(
                        'object named "'
                        + matches.group(1)
                        + '" was found but not added')

                self.data[matches.group(1)][matches.group(2)] = value
        return self.data


    def reset(self):
        self.data = {}
        for object in self.__objects:
            self.data[object] = {}
