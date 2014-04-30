# ----- Info ------------------------------------------------------------------

__author__ = 'Michael Montero <mcmontero@gmail.com>'

# ----- Imports ---------------------------------------------------------------

from tinyAPI.base.services.data import Marshaller
from tinyAPI.base.services.data import Validator
from tinyAPI.base.services.exception import MarshallerException

import tinyAPI
import unittest

# ----- Tests -----------------------------------------------------------------

class DataTestCase(unittest.TestCase):

    def test_marshaller_exceptions(self):
        try:
            Marshaller().add_object('b').format({'__a__one': 1})
        except MarshallerException as e:
            self.assertEqual(
                'object named "a" was found but not added',
                e.get_message())


    def test_marshaller(self):
        marshaller = Marshaller().add_object('a').add_object('b')

        record = {
            '__a__one': 1,
            '__b__two': 2,
            'three': 3
        }

        marshaller.format(record)
        self.assertTrue('a' in marshaller.data)
        self.assertTrue('b' in marshaller.data)
        self.assertTrue('three' in marshaller.data)
        self.assertTrue('one' in marshaller.data['a'])
        self.assertTrue('two' in marshaller.data['b'])
        self.assertEqual(1, marshaller.data['a']['one'])
        self.assertEqual(2, marshaller.data['b']['two'])
        self.assertEqual(3, marshaller.data['three'])


    def test_non_valid_email_addresses(self):
        invalid = [
            '',
            'email',
            'a@',
            '@b.com',
            'a!@b.com',
            'a@b',
            'a@b!.com',
            'a@b.invalidtld',
            'a@.com',
            'a@...com',
            'a@b.c^.com',
            'a@b.c',
            'a@b.com@d.com'
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
            'a@b.c.d.com'
        ]

        for em_address in valid:
            self.assertTrue(Validator().email_is_valid(em_address))

# ----- Main ------------------------------------------------------------------

if __name__ == '__main__':
    unittest.main()
