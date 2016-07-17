# ----- Info ------------------------------------------------------------------

__author__ = 'Michael Montero <mcmontero@gmail.com>'

# ----- Imports ---------------------------------------------------------------

from tinyAPI.base.services.imagemagick import ImageMagick

import tinyAPI
import unittest

# ----- Tests -----------------------------------------------------------------

class ImageMagickTestCase(unittest.TestCase):

    def test_get_geometry_error(self):
        try:
            ImageMagick().get_geometry('/a/b/c.jpg')

            self.fail('Was able to get geometry even though the file '
                      + 'provided does not exist.')
        except RuntimeError as e:
            self.assertEqual('could not find file "/a/b/c.jpg"', str(e))


    def test_get_geometry(self):
        file_name = '/opt/tinyAPI/base/services/tests/files/image.jpg'
        width, height = ImageMagick().get_geometry(file_name)

        self.assertEqual(2000, width)
        self.assertEqual(1338, height)

# ----- Main ------------------------------------------------------------------

if __name__ == '__main__':
    unittest.main()
