# ----- Info ------------------------------------------------------------------

__author__ = 'Michael Montero <mcmontero@gmail.com>'

# ----- Imports ---------------------------------------------------------------

import re
import subprocess

__all__ = [
    'ImageMagick'
]

# ----- Public Classes --------------------------------------------------------

class ImageMagick(object):
    '''Provides a wrapper to the ImageMagick binary.'''

    CONVERT = '/usr/bin/convert'

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
