# ----- Info ------------------------------------------------------------------

__author__ = 'Michael Montero <mcmontero@gmail.com>'

# ----- Imports ---------------------------------------------------------------

from .exception import MarshallerException

import re

__all__ = [
    'Marshaller',
    'Validator'
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


class Validator(object):
    '''Provides functionality for validating various types of data.'''

    def email_is_valid(self, em_address):
        try:
            name, domain = em_address.split('@')
        except ValueError:
            return False

        if len(name) == 0 or \
           len(domain) == 0 or \
           not re.search('^[A-Za-z0-9\._%+-]+$', name):
            return False

        domain_parts = domain.split('.')
        if len(domain_parts) < 2:
            return False

        for domain_part in domain_parts:
            if not re.search('^[A-Za-z0-9-_]+$', domain_part):
                return False

        # Attempt to validate the top level domain - .com, .org, .net, etc.
        if not re.search('^[A-Za-z]{2,6}$', domain_parts[-1]):
            return False

        return True
