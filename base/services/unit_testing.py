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

                failed = False
                for line in output.split("\n"):
                    if re.search('^test_', line) is not None:
                        test_case = ''
                        matches = re.search(' \(.*?\.(.*?)\)', line)
                        if matches is not None:
                            test_case = matches.group(1)

                        parts = line.split(' ')
                        if len(parts) == 4:
                            method_name = parts[0]
                            message = parts[3]
                        else:
                            raise RuntimeError(
                                '\n{}\n{}::{}\n\nproduced\n\n{}\n{}'
                                    .format(
                                        '=' * 75,
                                        test_case,
                                        parts[0],
                                        ' '.join(parts[3:]),
                                        '=' * 75
                                    )
                            )

                        if method_name is not None and method_name != line:
                            length = len(test_case) + len(method_name) + 12
                            if length > 79:
                                method_name = \
                                    '...' + method_name[(length - 76):]

                        self.__cli.notice(
                            '{}::{} .. {}'
                                .format(
                                    test_case,
                                    method_name,
                                    message
                                ),
                            1
                        )
                    elif line == 'OK':
                        self.__cli.notice('', 1)
                    elif line != '':
                        self.__cli.notice(line, 1)

                    matches = re.match('Ran (\d+) test', line)
                    if matches is not None:
                        self.__total_tests += int(matches.group(1))

                    if re.match('FAILED \(', line) or re.search('Error:', line):
                        failed = True

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
            tinyAPI.dsh().select_db(default_connection, default_schema)

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
