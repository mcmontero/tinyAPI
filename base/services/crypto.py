# ----- Info ------------------------------------------------------------------

__author__ = 'Michael Montero <mcmontero@gmail.com>'

# ----- Imports ---------------------------------------------------------------

from Crypto import Random
from Crypto.Cipher import AES
from .exception import CryptoException

import base64
import hashlib
import json
import time

__all__ = [
    'DataArmor'
]

# ----- Public Classes --------------------------------------------------------

class DataArmor(object):
    '''Creates an encrypted token that cannot be modified without detection and
       can be expired by TTL.'''

    def __init__(self, key, data):
        key_len = len(key)
        if key_len != 16 and key_len != 24 and key_len != 32:
            raise CryptoException(
                'key must be of length 16, 24, or 32 bytes')

        self.__key = key
        self.__data = data
        self.timestamp = None


    def __decrypt(self, data):
        data = base64.b64decode(data.encode(), b'|_')
        iv = data[:AES.block_size]
        cipher = AES.new(self.__key, AES.MODE_CBC, iv)

        return self.__unpad(cipher.decrypt(data[AES.block_size:]))


    def __encrypt(self, data):
        data = self.__pad(data)
        iv = Random.new().read(AES.block_size)
        cipher = AES.new(self.__key, AES.MODE_CBC, iv)

        return base64.b64encode(iv + cipher.encrypt(data), b'|_')


    def lock(self):
        '''Secure the data.'''
        data = json.dumps(self.__data)

        timestamp = \
            str \
            (
                int(time.time())
                    if self.timestamp is None else
                self.timestamp
            )

        sha = \
            hashlib.sha224(
                data.encode('utf8') +
                timestamp.encode('utf8')
            ) \
                .hexdigest()

        data = data + chr(2) + timestamp

        return self.__encrypt(data).decode() + '-' + sha


    def __pad(self, data):
        bs = AES.block_size
        return data + (bs - len(data) % bs) * chr(bs - len(data) % bs)


    def set_timestamp(self, timestamp):
        self.timestamp = timestamp
        return self


    def unlock(self, ttl=None):
        '''Decrypt the data and return the original payload.'''
        parts = self.__data.split('-')

        try:
            data = self.__decrypt(parts[0]).decode()
        except:
            raise CryptoException(
                'data failed to decrypt; contents were likely tampered with')

        sha = parts[1]

        parts = data.split(chr(2))
        data = parts[0]

        try:
            self.timestamp = int(parts[1])
        except IndexError:
            raise CryptoException(
                'could not find timestamp; encryption key was likely incorrect')

        if hashlib.sha224(
            data.encode('utf8') + str(self.timestamp).encode('utf8')
           ) \
            .hexdigest() != sha:
                raise CryptoException('armored token has been tampered with');

        if ttl is not None:
            if (int(time.time()) - self.timestamp) > ttl:
                raise CryptoException('token has expired')

        return json.loads(data)


    def __unpad(self, data):
        return data[:-ord(data[len(data) - 1:])]
