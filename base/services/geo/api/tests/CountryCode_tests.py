# ----- Info ------------------------------------------------------------------

__author__ = 'Michael Montero <mcmontero@gmail.com>'

# ----- Imports ---------------------------------------------------------------

from tinyAPI.base.services.geo.api.CountryCode import CountryCode

import tinyAPI
import unittest

# ----- Tests -----------------------------------------------------------------

class CountryCodeTestCase(unittest.TestCase):

    def test_get_errors(self):
        try:
            CountryCode().get(-1)

            self.fail('Was able to get country code even though the ID '
                      + 'provided was invalid.')
        except RuntimeError as e:
            self.assertEqual('no such country code ID "-1"', str(e))


    def test_get_country_name_errors(self):
        try:
            CountryCode().get_country_name(-1)

            self.fail('Was able to get country name even though the ID '
                      + 'provided was invalid.')
        except RuntimeError as e:
            self.assertEqual('no such country code ID "-1"', str(e))


    def test_get(self):
        self.assertEqual("1", CountryCode().get(213))


    def test_get(self):
        self.assertEqual("United States", CountryCode().get_country_name(213))


# ----- Main ------------------------------------------------------------------

if __name__ == '__main__':
    unittest.main()
