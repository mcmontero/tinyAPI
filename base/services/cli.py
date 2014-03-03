'''cli.py -- Command line interface functionality for programs.'''

__author__ = 'Michael Montero <mcmontero@gmail.com>'

# ----- Imports --------------------------------------------------------------

from .exception import CLIException
import argparse
import errno
import datetime
import os
import re
import sys
import time

# ----- Public Functions  ----------------------------------------------------

def cli_main(function, args=None):
    '''Executes the "main" CLI function passing in the configured arguments.'''
    cli = CLI(args)
    try:
        function(cli)
    except:
        cli.set_status_error()
        raise

# ----- Public Classes  ------------------------------------------------------

class CLI(object):
    '''Provides methods for executing and managing CLI programs.'''

    STATUS_OK = 1
    STATUS_WARN = 2;
    STATUS_ERROR = 3;

    args = None
    __enable_status = False
    __pid_lock_file = None
    __started = int(time.time())
    __status_id = STATUS_OK

    def __init__(self, args=None):
        if args is not None:
            if not isinstance(args, argparse.ArgumentParser):
                raise CLIException('args much be instance of ArgumentParser')
            self.args = args.parse_args()

        self.__pid_lock()
        self.__enable_status = True

    def __del__(self):
        if self.__enable_status:
            self.status()

        if self.__pid_lock_file is not None:
            try:
                os.remove(self.__pid_lock_file)
            except OSError as e:
                if e.errno != errno.ENOENT:
                    raise

    def error(self, message, indent=None):
        '''Outputs an error message.'''
        self.__status_id = self.STATUS_ERROR
        self.__print_message(message, '!', indent)

    def exit(self):
        '''Exits setting the return value based on the status of the CLI.'''
        exit(0 if self.__status_id == self.STATUS_OK else 1)

    def header(self, title):
        '''Displays the header of the CLI containing the name.'''
        print("\n" + CLIOutputRenderer().draw_header(title))

    def notice(self, message, indent=None):
        '''Outputs a notice message.'''
        self.__print_message(message, '+', indent)

    def __pid_lock(self):
        params = []
        params_str = '';
        if self.args is not None:
            params = list(filter(None, list(vars(self.args).values())))
            params_str = ' '.join(str(v) for v in params)

        base_name = '/var/run/cli/' + os.path.basename(sys.argv[0])

        if len(params) > 0:
            base_name += '-' + re.sub('[^A-Za-z0-9]', '', params_str)

        self.__pid_lock_file = base_name + '.pid_lock'

        try:
            pid_file = os.fdopen(os.open(self.__pid_lock_file,
                                         os.O_CREAT | os.O_EXCL | os.O_WRONLY,
                                         0o644),
                                 'w')
        except OSError as e:
            if e.errno == errno.EEXIST:
                self.__pid_lock_failed()

        pid_file.write(str(os.getpid()))
        pid_file.close()

    def __pid_lock_failed(self):
        self.__enable_status = False;

        print("\n* Process is already running!")
        print("* Could not acquire PID lock on:\n    " + self.__pid_lock_file)

        with open(self.__pid_lock_file) as f:
            print("* The lock is held by PID " + f.read() + '.\n')

        self.__pid_lock_file = None
        sys.exit(0);

    def __print_message(self, message, char, indent=None):
        if indent is not None:
            print((' ' * 4) + message)
        else:
            print(char + ' ' + message)

    def set_status_error(self):
        self.__status_id = self.STATUS_ERROR

    def status(self):
        '''Prints a final message about the overall status of a CLI when it
           exits.'''
        elapsed = int(time.time()) - self.__started
        indicator = '';
        message = '';
        if self.__status_id == self.STATUS_OK:
            indicator = '+'
            message = 'successfully'
        elif self.__status_id == self.STATUS_WARN:
            indicator = '*'
            message = 'with warnings'
        elif self.__status_id == self.STATUS_ERROR:
            indicator = '!'
            message = 'with errors'

        print(("\n" + indicator + ' Execution completed ' + message
               + ' in ' + str('{0:,}'.format(elapsed)) + "s!\n"))

    def time_marker(self, num_iterations=None):
        '''Outputs the time for each iteration of a CLI that runs in a loop
           continuously.'''
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
