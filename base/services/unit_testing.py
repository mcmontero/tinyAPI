'''unit_testing.py -- Provides functionality for putting standards and
   consistency around executing unit tests.'''

__author__ = 'Michael Montero <mcmontero@gmail.com>'

# ----- Imports --------------------------------------------------------------

import re
import subprocess
import sys
import time

# ----- Public Classes  ------------------------------------------------------

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

                output = subprocess.check_output(
                    "/usr/bin/python3 " + file + " -v ; exit 0",
                    stderr=subprocess.STDOUT,
                    shell=True).decode();

                failed = False
                for line in output.split("\n"):
                    test_case = ''
                    matches = re.search(' \(.*?\.(.*?)\)', line)
                    if matches is not None:
                        test_case = matches.group(1) + '::'

                    self.__cli.notice(
                        test_case + re.sub(' \(.*?\..*?\)', '', line), 1)

                    matches = re.match('Ran (\d+) test', line)
                    if matches is not None:
                        self.__total_tests += int(matches.group(1))

                    if re.match('FAILED \(', line):
                        failed = True

                if failed is True:
                    sys.exit(1)

        self.__total_run_time += time.time() - file_run_time_start;

    def print_summary(self):
        self.__cli.notice('  Total number of tests executed: '
                          + str('{0:,}'.format(self.__total_tests)))
        self.__cli.notice('Total elapsed time for all tests: '
                          + str(self.__total_run_time))

__all__ = ['Manager']
