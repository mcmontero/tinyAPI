# ----- Info ------------------------------------------------------------------

__author__ = 'Michael Montero <mcmontero@gmail.com>'

# ----- Imports ---------------------------------------------------------------

import re
import subprocess

__all__ = [
    'Ffmpeg'
]

# ----- Public Classes --------------------------------------------------------

class Ffmpeg(object):
    '''Provides a wrapper to the ffmpeg binary.'''

    FFPROBE = '/usr/local/bin/ffprobe'

    def __init__(self, video_file_path):
        self.video_file_path = video_file_path
        self.width = None
        self.height = None
        self.duration = None


    def get_duration(self):
        if self.duration is None:
            process = \
                subprocess.Popen(
                    [self.FFPROBE,
                     '-v',
                     'error',
                     '-of',
                     'default=noprint_wrappers=1:nokey=1',
                     '-select_streams',
                     'v:0',
                     '-show_entries',
                     'stream=duration',
                     self.video_file_path],
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE)

            self.duration = \
                int(round(float(process.stdout.readline().decode())))

        return self.duration


    def get_geometry(self):
        if self.width is None or self.height is None:
            process = \
                subprocess.Popen(
                    [self.FFPROBE,
                     '-v',
                     'error',
                     '-of',
                     'default=noprint_wrappers=1:nokey=1',
                     '-select_streams',
                     'v:0',
                     '-show_entries',
                     'stream=height,width',
                     self.video_file_path],
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE)

            self.width = int(process.stdout.readline().decode())
            self.height = int(process.stdout.readline().decode())

        return self.width, self.height
