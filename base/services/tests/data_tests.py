# ----- Info ------------------------------------------------------------------

__author__ = 'Michael Montero <mcmontero@gmail.com>'

# ----- Imports ---------------------------------------------------------------

from tinyAPI.base.services.data import Serializer
from tinyAPI.base.services.data import Validator
from tinyAPI.base.services.exception import SerializerException

import phonenumbers
import tinyAPI
import unittest

# ----- Tests -----------------------------------------------------------------

class DataTestCase(unittest.TestCase):

    def test_serializer_errors(self):
        try:
            Serializer().to_json({'__abc__': 123})

            self.fail('Was able to format a record to JSON even though no '
                      + 'variable was defined.')
        except SerializerException as e:
            self.assertEqual('could not format to JSON for key "__abc__"',
                             e.get_message())


    def test_serializer_simple(self):
        data = Serializer().to_json({'abc': 123})
        self.assertTrue('abc' in data)
        self.assertEqual(123, data['abc'])


    def test_serializer_single(self):
        data = Serializer().to_json({'__one__two': 123})
        self.assertTrue('one' in data)
        self.assertTrue('two' in data['one'])
        self.assertEqual(123, data['one']['two'])


    def test_serializer_double(self):
        data = Serializer().to_json({'__one____two__three': 123})
        self.assertTrue('one' in data)
        self.assertTrue('two' in data['one'])
        self.assertTrue('three' in data['one']['two'])
        self.assertEqual(123, data['one']['two']['three'])


    def test_serializer_triple(self):
        data = Serializer().to_json({'__one____two____three__four': 123})
        self.assertTrue('one' in data)
        self.assertTrue('two' in data['one'])
        self.assertTrue('three' in data['one']['two'])
        self.assertTrue('four' in data['one']['two']['three'])
        self.assertEqual(123, data['one']['two']['three']['four'])


    def test_non_valid_email_addresses(self):
        invalid = [
            '',
            'email',
            'a@',
            '@b.com',
            'a!@b.com',
            'a@b',
            'a@b!.com',
            'a@.com',
            'a@...com',
            'a@b.c^.com',
            'a@b.c',
            'a@b.com@d.com',
            ' a@b.com',
            'a@b.com ',
            'a@b.com\n',
            'a@\nb.com'
        ]

        for em_address in invalid:
            self.assertFalse(Validator().email_is_valid(em_address))


    def test_valid_email_addresses(self):
        valid = [
            'a@b.com',
            'a+b_c@d.com',
            'a.b@c.com',
            'a%b@c.com',
            'a12345@b.com',
            'A@B.COM',
            'a@b.c.d.com',
            'abc@a-b.c.org',
            'a@b.solutions'
        ]

        for em_address in valid:
            self.assertTrue(Validator().email_is_valid(em_address))


    def test_serializer_to_json_none(self):
        self.assertIsNone(Serializer().to_json(None))


    def test_serializer_to_json_depth_errors(self):
        try:
            Serializer().to_json({'__a____b____c____d____e__f': 123})

            self.fail('Was able to serialize to JSON even though the depth '
                      + 'is not supported.')
        except SerializerException as e:
            self.assertEqual(
              'depth of 11 not supported for key "__a____b____c____d____e__f"',
              e.get_message())


    def test_latitude_is_valid(self):
        self.assertTrue(Validator().latitude_is_valid(-90.00))
        self.assertTrue(Validator().latitude_is_valid(90.00))
        self.assertFalse(Validator().latitude_is_valid(-90.01))
        self.assertFalse(Validator().latitude_is_valid(90.01))


    def test_longitude_is_valid(self):
        self.assertTrue(Validator().longitude_is_valid(-180.00))
        self.assertTrue(Validator().longitude_is_valid(180.00))
        self.assertFalse(Validator().longitude_is_valid(-180.01))
        self.assertFalse(Validator().longitude_is_valid(180.01))


    def test_non_us_phone_number(self):
        p = phonenumbers.parse('+442083661177', None)
        self.assertEqual(44, p.country_code)
        self.assertEqual(2083661177, p.national_number)


    def test_us_phone_number(self):
        p = phonenumbers.parse('+17184734811', None)
        self.assertEqual(1, p.country_code)
        self.assertEqual(7184734811, p.national_number)


    def test_is_valid_number(self):
        p = phonenumbers.parse('+1123456789')
        self.assertFalse(phonenumbers.is_possible_number(p))
        self.assertFalse(phonenumbers.is_valid_number(p))

        p = phonenumbers.parse('+17184734811')
        self.assertTrue(phonenumbers.is_possible_number(p))
        self.assertTrue(phonenumbers.is_valid_number(p))


    def test_formatting_e164(self):
        p = phonenumbers.parse('+17184734811')
        self.assertEqual(
            '+17184734811',
            phonenumbers.format_number(p, phonenumbers.PhoneNumberFormat.E164)
        )


    def test_phone_number_is_valid(self):
        self.assertFalse(Validator().phone_number_is_valid('+11234567890'))
        self.assertTrue(Validator().phone_number_is_valid('+17184734811'))

# ----- Main ------------------------------------------------------------------

if __name__ == '__main__':
    unittest.main()
