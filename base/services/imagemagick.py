# ----- Info ------------------------------------------------------------------

__author__ = 'Michael Montero <mcmontero@gmail.com>'

# ----- Imports ---------------------------------------------------------------

import os
import re
import subprocess

__all__ = [
    'ImageMagick'
]

# ----- Public Classes --------------------------------------------------------

class ImageMagick(object):
    '''Provides a wrapper to the ImageMagick binary.'''

    CONVERT = '/usr/bin/convert'
    IDENTIFY = '/usr/bin/identify'

    def get_geometry(self, file_name):
        if not os.path.isfile(file_name):
            raise RuntimeError(
                'could not find file "{}"'
                    .format(file_name)
            )

        output = \
            subprocess.check_output(
                [self.IDENTIFY,
                 file_name]
            )

        matches = re.search('(\d+)x(\d+)\+', output.decode())
        if not matches:
            raise RuntimeError(
                'could not determine geometry for file "{}"'
                    .format(file_name)
            )

        return int(matches.group(1)), int(matches.group(2))


    def resize(self, source, width, height, destination):
        process = \
            subprocess.Popen(
                [self.CONVERT,
                 '-geometry',
                 '{}x{}'.format(width, height),
                 source,
                 destination],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )

        error = process.stderr.readline().decode()
        if len(error) > 0:
            raise RuntimeError(error)
