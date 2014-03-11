'''data_armor.py -- Allows for the creation of secure, encrypted packets of
   data.  It is highly recommended that you use a key length of 32 bytes.'''

__author__ = 'Michael Montero <mcmontero@gmail.com>'

# ----- Import ----------------------------------------------------------------

from Crypto import Random
from Crypto.Cipher import AES
from .exception import CryptoException
import base64
import hashlib
import json
import time

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

    def __decrypt(self, data):
        data = base64.b64decode(data.encode())
        iv = data[:AES.block_size]
        cipher = AES.new(self.__key, AES.MODE_CBC, iv)

        return self.__unpad(cipher.decrypt(data[AES.block_size:]))

    def __encrypt(self, data):
        data = self.__pad(data)
        iv = Random.new().read(AES.block_size)
        cipher = AES.new(self.__key, AES.MODE_CBC, iv)

        return base64.b64encode(iv + cipher.encrypt(data))

    def lock(self):
        '''Secure the data.'''
        data = json.dumps(self.__data)
        now = str(int(time.time()))
        sha = hashlib.sha224(data.encode('utf8') +
                             now.encode('utf8')).hexdigest()
        data = data + chr(2) + now

        return self.__encrypt(data).decode() + '-' + sha

    def __pad(self, data):
        bs = AES.block_size
        return data + (bs - len(data) % bs) * chr(bs - len(data) % bs)

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
        timestamp = parts[1]

        if hashlib.sha224(
            data.encode('utf8') + timestamp.encode('utf8')).hexdigest() != sha:
                raise CryptoException('armored token has been tampered with');

        if ttl is not None:
            if (int(time.time()) - int(timestamp)) > ttl:
                raise CryptoException('token has expired')

        return json.loads(data)

    def __unpad(self, data):
        return data[:-ord(data[len(data) - 1:])]

__all__ = ['DataArmor']
