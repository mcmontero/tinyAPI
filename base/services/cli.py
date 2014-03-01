'''cli.py -- Command line interface functionality for programs.'''

__author__ = 'Michael Montero <mcmontero@gmail.com>'

# ----- Imports --------------------------------------------------------------

from .exception import CLIException
import argparse
import datetime
import sys
import time

# ----- Public Functions  ----------------------------------------------------

def cli_main(args, function):
    '''Executes the "main" CLI function passing in the configured arguments.'''
    function(CLI(args))

# ----- Public Classes  ------------------------------------------------------

class CLI(object):
    '''Provides methods for executing and managing CLI programs.'''

    STATUS_OK = 1
    STATUS_WARN = 2;
    STATUS_ERROR = 3;

    args = None
    __started = None
    __status_id = STATUS_OK

    def __init__(self, args):
        if not isinstance(args, argparse.ArgumentParser):
            raise CLIException('args much be instance of ArgumentParser')

        self.args = args.parse_args()
        self.__started = int(time.time())

    def __del__(self):
        self.status()

    def draw_header(self, title):
        '''Displays the header of the CLI containing the name.'''
        print("\n" + CLIOutputRenderer().draw_header(title))

    def error(self, message, indent=None):
        '''Outputs an error message.'''
        self.__status_id = self.STATUS_ERROR
        self.__print_message(message, '!', indent)

    def exit(self):
        '''Exits setting the return value based on the status of the CLI.'''
        exit(0 if self.__status_id == self.STATUS_OK else 1)

    def notice(self, message, indent=None):
        '''Outputs a notice message.'''
        self.__print_message(message, '+', indent)

    def __print_message(self, message, char, indent=None):
        if indent is not None:
            print((' ' * 4) + message)
        else:
            print(char + ' ' + message)

    def status(self):
        elapsed = int(time.time()) - self.__started
        indicator = '';
        message = '';
        if self.__status_id == self.STATUS_OK:
            indicator = '+'
            mesage = 'successfully'
        elif self.__status_id == self.STATUS_WARN:
            indicator = '*'
            message = 'with warnings'
        elif self.__status_id == self.STATUS_ERROR:
            indicator = '!'
            message = 'with errors'

        print(("\n" + indicator + ' Execution completed ' + message
               + ' in ' + str('{0:,}'.format(elapsed)) + "s!\n"))

    def time_marker(self, num_iterations=None):
        self.notice(
            ('----- Marker '
             + (str(num_iterations) if num_iterations is not None else '')
             + ' ['
             + str(datetime.datetime.now())
             + ']'))

    def warn(self, message, indent=None):
        '''Outputs a warning message.'''
        self.__print_message(message, '*', indent)


class CLIOutputRenderer(object):
    '''Provides methods for consistent output from CLI programs.'''

    @staticmethod
    def draw_header(title, width=79):
        enclosure = '# +' + ('-' * (width - 5)) + "+\n"
        body = '# | ' + title
        body += ' ' * (width - 2 - len(body)) + "|\n"

        return enclosure + body + enclosure

__all__ = ['CLI', 'cli_main', 'CLIOutputRenderer']
