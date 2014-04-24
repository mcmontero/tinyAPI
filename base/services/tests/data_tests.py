# ----- Info ------------------------------------------------------------------

__author__ = 'Michael Montero <mcmontero@gmail.com>'

# ----- Import ----------------------------------------------------------------

from tinyAPI.base.services.data import Marshaller
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

# ----- Main ------------------------------------------------------------------

if __name__ == '__main__':
    unittest.main()
