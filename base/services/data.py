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

    def __add(self, entity, data=tuple()):
        if entity not in data:
            data[entity] = {}

        return data


    def to_json(self, record=tuple()):
        if record is None:
            return None

        self.data = {}

        for key, value in record.items():
            parts = key.split('__')
            count = len(parts)

            if parts[-1] == '':
                raise SerializerException(
                    'could not format to JSON for key "{}"'
                        .format(key))

            if count == 1:
                self.data[key] = value
            elif count == 3:
                self.__add(parts[1], self.data)

                self.data \
                    [parts[1]] \
                    [parts[2]] = value
            elif count == 5:
                self.__add(
                    parts[1],
                    self.data)
                self.__add(
                    parts[3],
                    self.data[parts[1]])

                self.data \
                    [parts[1]] \
                    [parts[3]] \
                    [parts[4]] = value
            elif count == 7:
                self.__add(
                    parts[1],
                    self.data)
                self.__add(
                    parts[3],
                    self.data[parts[1]])
                self.__add(
                    parts[5],
                    self.data[parts[1]][parts[3]])

                self.data \
                    [parts[1]] \
                    [parts[3]] \
                    [parts[5]] \
                    [parts[6]] = value
            elif count == 9:
                self.__add(
                    parts[1],
                    self.data)
                self.__add(
                    parts[3],
                    self.data[parts[1]])
                self.__add(
                    parts[5],
                    self.data[parts[1]][parts[3]])
                self.__add(
                    parts[7],
                    self.data[parts[1]][parts[3]][parts[5]])

                self.data \
                    [parts[1]] \
                    [parts[3]] \
                    [parts[5]] \
                    [parts[7]] \
                    [parts[8]] = value
            else:
                raise SerializerException(
                    'depth of {} not supported for key "{}"'
                        .format(count, key))

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


    def latitude_is_valid(self, latitude):
        return latitude < -90.00 or latitude > 90.00


    def longitude_is_valid(self, longitude):
        return longitude < -180.00 or longitude > 180.00
