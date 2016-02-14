# ----- Info ------------------------------------------------------------------

__author__ = 'Michael Montero <mcmontero@gmail.com>'

# ----- Imports ---------------------------------------------------------------

from tinyAPI.base.services.queue.fs import FileSystemQueue

import glob
import os
import re
import tinyAPI
import unittest

# ----- Tests -----------------------------------------------------------------

class QueueFSTestCase(unittest.TestCase):

    def __clean_up_files(self):
        files = glob.glob(os.path.join('/tmp', 'ut-*'))
        for file in files:
            os.unlink(file)


    def setUp(self):
        self.__clean_up_files()

        self.fsq = FileSystemQueue('/tmp', 'ut')


    def tearDown(self):
        self.__clean_up_files()


    def test_dequeue_no_such_file(self):
        self.fsq.dequeue('abc')


    def test_enqueue(self):
        queue_file = self.fsq.enqueue({'a': 'b'})
        self.assertIsNotNone(
            queue_file
        )
        self.assertTrue(
            re.search(
                '^ut-[\d]+-[a-zA-Z0-9]+$',
                os.path.basename(queue_file)
            )
        )


    def test_get(self):
        queue_file = self.fsq.enqueue({'a': 'b'})
        self.assertIsNotNone(queue_file)

        queue = self.fsq.get()
        self.assertEqual(1, len(queue))
        self.assertEqual({'a': 'b'}, queue[0]['data'])
        self.assertFalse(os.path.isfile(queue_file))


    def test_get_dont_remove_queue_file_dequeue(self):
        queue_file = self.fsq.enqueue({'a': 'b'})
        self.assertIsNotNone(queue_file)

        queue = self.fsq.get(False)
        self.assertEqual(1, len(queue))
        self.assertEqual({'a': 'b'}, queue[0]['data'])
        self.assertTrue(os.path.isfile(queue_file))

        self.fsq.dequeue(queue_file)
        self.assertFalse(os.path.isfile(queue_file))

# ----- Main ------------------------------------------------------------------

if __name__ == '__main__':
    unittest.main()
