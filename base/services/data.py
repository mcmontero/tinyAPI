# ----- Info ------------------------------------------------------------------

__author__ = 'Michael Montero <mcmontero@gmail.com>'

# ----- Imports ---------------------------------------------------------------

from .exception import SerializerException

import re

__all__ = [
    'Serializer',
    'Validator'
]

# ----- Public Classes --------------------------------------------------------

class Serializer(object):
    '''Serializes formatted SQL results for transportation via REST API.'''

    def __add_object(self, key, value, path, elem, objects=tuple()):
        if objects[0] not in elem:
            elem[objects[0]] = {}

        path += '__' + objects[0] + '__'

        if len(objects) == 1:
            var = re.sub(path, '', key)
            if len(var) == 0:
                raise SerializerException(
                    'could not format to JSON for key "' + key + '"')

            elem[objects[0]][var] = value

            return

        self.__add_object(key, value, path, elem[objects[0]], objects[1:])


    def to_json(self, record=tuple()):
        self.data = {}

        for key, value in record.items():
            objects = re.findall('__([A-Za-z0-9_]+?)__', key)
            if len(objects) == 0:
                self.data[key] = value
            else:
                self.__add_object(key, value, '', self.data, objects)

        return self.data


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
