# ----- Info ------------------------------------------------------------------

__author__ = 'Michael Montero <mcmontero@gmail.com>'

# ----- Imports ---------------------------------------------------------------

from tinyAPI.base.services.ffmpeg import Ffmpeg

import tinyAPI
import unittest

# ----- Tests -----------------------------------------------------------------

class FfmpegTestCase(unittest.TestCase):

    def test_get_geometry(self):
        ffmpeg = Ffmpeg('/opt/tinyAPI/base/services/tests/files/video.mov')
        width, height = ffmpeg.get_geometry()

        self.assertEqual(160, width)
        self.assertEqual(120, height)
        self.assertEqual(160, ffmpeg.width)
        self.assertEqual(120, ffmpeg.height)


    def test_get_duration(self):
        ffmpeg = Ffmpeg('/opt/tinyAPI/base/services/tests/files/video.mov')
        duration = ffmpeg.get_duration()

        self.assertEqual(13, duration)

# ----- Main ------------------------------------------------------------------

if __name__ == '__main__':
    unittest.main()
