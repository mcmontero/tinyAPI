# ----- Info ------------------------------------------------------------------

__author__ = 'Michael Montero <mcmontero@gmail.com>'

# ----- Imports ---------------------------------------------------------------

from tinyAPI.base.config import ConfigManager
from tinyAPI.base.context import Context

import re
import subprocess
import sys
import time
import tinyAPI
import unittest

__all__ = [
    'Manager',
    'TransactionalDataStoreTestCase'
]

# ----- Public Classes  -------------------------------------------------------

class Manager(object):
    '''Provides methods for executing and reporting on unit tests.'''

    def __init__(self, cli):
        self.__cli = cli
        self.__enable_stop_on_failure = True
        self.__total_run_time = 0
        self.__total_tests = 0


    def disable_stop_on_failure(self):
        self.__enable_stop_on_failure = False
        return self


    def execute(self, files=tuple()):
        for file in files:
            if file != '':
                self.__cli.notice(file + "\n")

                file_run_time_start = time.time()
                num_file_tests = 0

                output = \
                    subprocess.check_output(
                        "export ENV_UNIT_TEST=1 ; "
                        + sys.executable + " " + file + " -v ; "
                        + "exit 0",
                        stderr=subprocess.STDOUT,
                        shell=True
                    ) \
                        .decode();

                failed = flush = False
                test_info = None
                for line in output.split("\n"):
                    # Attempt to capture test results
                    results = re.search(r' \.\.\. (?P<output>.*)(?P<message>ok|fail|error|skipped)$', line, re.IGNORECASE)
                    if test_info is None:
                        test_info = re.match(r'^(?P<method>test_[^ ]+) \(.*?\.(?P<class>.*?)\)', line)
                        if test_info is not None:
                            flush = False

                    if re.match('FAILED \(', line) or re.search('Error:', line):
                        flush = True
                        failed = True

                    # If results delimiter is found we need to validate case output
                    if results is not None:
                        test_class = test_method = message = ''
                        if test_info is not None:
                            test_method = test_info.group('method')
                            test_class = test_info.group('class')
                            message = results.group('message')

                        # Validate that no output occured
                        if results.group('output'):
                            raise RuntimeError(
                                '\n{}\n{}::{}\n\nproduced\n\n{}\n{}'
                                    .format(
                                        '=' * 75,
                                        test_class,
                                        test_method,
                                        results.group('output'),
                                        '=' * 75
                                    )
                            )
                        else:
                            if test_method is not None and test_method != line:
                                length = len(test_class) + len(test_method) + 12
                                if length > 79:
                                    test_method = \
                                        '...' + test_method[(length - 76):]

                            self.__cli.notice(
                                '{}::{} .. {}'
                                    .format(
                                        test_class,
                                        test_method,
                                        message.upper()
                                    ),
                                1
                            )

                            # We've already caught the end the current test
                            # Flush the rest of the incoming lines before the next test
                            flush = True
                            test_info = results = None
                            test_method = test_class = message = ''
                    elif line == 'OK':
                        self.__cli.notice('', 1)
                    elif line != '' and flush:
                        self.__cli.notice(line, 1)

                    matches = re.match('Ran (\d+) test', line)
                    if matches is not None:
                        self.__total_tests += int(matches.group(1))

                if failed is True:
                    sys.exit(1)

                self.__total_run_time += time.time() - file_run_time_start;


    def print_summary(self):
        self.__cli.notice('  Total number of tests executed: '
                          + str('{0:,}'.format(self.__total_tests)))
        self.__cli.notice('Total elapsed time for all tests: '
                          + str(self.__total_run_time))


class TransactionalDataStoreTestCase(unittest.TestCase):
    '''Provides a test case for transactional data stores that rolls back
       changes after each unit test.'''

    def setUp(self):
        default_schema = ConfigManager.value('default schema')
        default_connection = ConfigManager.value('default unit test connection')
        if default_schema and default_connection:
            tinyAPI.dsh.select_db(default_connection, default_schema)

        self.maxDiff = None
        self.set_up()


    def set_up(self):
        pass


    def tearDown(self):
        self.tear_down()
        tinyAPI.dsh().rollback(True)


    def tear_down(self):
        pass

# ----- Instructions ----------------------------------------------------------

Context().set_unit_test()
