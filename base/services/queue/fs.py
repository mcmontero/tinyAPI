# ----- Info ------------------------------------------------------------------

__author__ = 'Michael Montero <mcmontero@gmail.com>'

# ----- Imports ---------------------------------------------------------------

import glob
import json
import os
import random
import re
import string
import time

# ----- Public Classes --------------------------------------------------------

class FileSystemQueue(object):
    '''Allows for queueing data to a file system queue.'''

    def __init__(self, queue_dir, domain=None):
        self.__queue_dir = queue_dir
        self.__domain = domain


    def enqueue(self, data=tuple()):
        file_name = self.__get_file_name()

        with open(file_name + '.writing', 'w') as f:
            f.write(json.dumps(data))

        os.rename(file_name + '.writing', file_name)

        return file_name


    def dequeue(self, queue_file_name):
        try:
            os.unlink(queue_file_name)
        except FileNotFoundError:
            pass

        return self


    def get(self, remove_queue_file=True):
        files = glob.glob(os.path.join(self.__queue_dir, '*'))
        if files is None or len(files) == 0:
            return None

        queue = []
        for file_path in sorted(files):
            if re.search('\.writing$', file_path):
                continue

            if self.__domain is not None:
                if not re.search(
                        '^' + self.__domain + '-',
                        os.path.basename(file_path)
                       ):
                    continue

            with open(file_path, 'r') as f:
                payload = f.read()
                if payload is not None and len(payload) > 0:
                    queue.append({
                        'file': file_path,
                        'data': json.loads(payload)
                    })

            if remove_queue_file is True:
                os.unlink(file_path)

        return queue if len(queue) > 0 else None


    def __get_file_name(self):
        file = '{}-{}'.format(int(time.time()), self.__random_string(32))
        if self.__domain is not None:
            file = self.__domain + '-' + file

        return '{}/{}'.format(self.__queue_dir, file)


    def __random_string(self, length):
        return \
            ''.join(
                random.choice(
                    string.ascii_lowercase +
                    string.ascii_uppercase +
                    string.digits
                )
                    for _ in range(length)
            )
