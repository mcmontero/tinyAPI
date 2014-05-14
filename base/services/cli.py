# ----- Info ------------------------------------------------------------------

__author__ = 'Michael Montero <mcmontero@gmail.com>'

# ----- Imports ---------------------------------------------------------------

from .exception import CLIException
from tinyAPI.base.config import ConfigManager

import argparse
import errno
import datetime
import logging
import os
import re
import sys
import time
import tinyAPI
import traceback

__all__ = [
    'CLI',
    'cli_main',
    'CLIOutputRenderer'
]

# ----- Definitions -----------------------------------------------------------

CLI_STOP_SIGNAL_FILE = '/tmp/APP_STOP_CLI'

# ----- Public Functions  -----------------------------------------------------

def cli_main(function, args=None, stop_on_signal=True):
    '''Executes the "main" CLI function passing in the configured arguments.'''
    if stop_on_signal and os.path.isfile(CLI_STOP_SIGNAL_FILE):
        raise CLIException( 'CLI execution has been stopped')

    cli = CLI(args)
    if not stop_on_signal:
        cli.dont_stop_on_signal()

    try:
        function(cli)
    except Exception as e:
        _handle_cli_exception_logging(e)

        cli.set_status_error()
        tinyAPI.dsh().rollback(True)
        tinyAPI.dsh().close()

        raise

# ----- Public Classes  -------------------------------------------------------

class CLI(object):
    '''Provides methods for executing and managing CLI programs.'''

    STATUS_OK = 1
    STATUS_WARN = 2;
    STATUS_ERROR = 3;

    def __init__(self, args=None):
        self.args = None
        if args is not None:
            if not isinstance(args, argparse.ArgumentParser):
                raise CLIException('args much be instance of ArgumentParser')
            self.args = args.parse_args()

        self.__enable_status = False
        self.__pid_lock_file = None
        self.__started = int(time.time())
        self.__status_id = self.STATUS_OK
        self.__stop_on_signal = True

        self.__pid_lock()
        # Now that PID locking has succeeded, enable the status.
        self.__enable_status = True


    def __del__(self):
        try:
            if self.__enable_status is True:
                self.status()
        except AttributeError:
            pass

        try:
            if self.__pid_lock_file is not None:
                try:
                    os.remove(self.__pid_lock_file)
                except OSError as e:
                    if e.errno != errno.ENOENT:
                        raise
        except AttributeError:
            pass


    def dont_stop_on_signal(self):
        self.__stop_on_signal = False
        return self


    def error(self, message, indent=None):
        '''Outputs an error message.'''
        self.__status_id = self.STATUS_ERROR
        self.__print_message(message, '!', indent)
        self.process_signals()


    def exit(self):
        '''Exits setting the return value based on the status of the CLI.'''
        exit(0 if self.__status_id == self.STATUS_OK else 1)


    def __get_active_pid(self):
        active_pid = None

        try:
           file = open(self.__pid_lock_file, 'r')
           active_pid = int(file.read())
           file.close()
        except FileNotFoundError:
            return None

        return active_pid


    def header(self, title):
        '''Displays the header of the CLI containing the name.'''
        print("\n" + CLIOutputRenderer().header(title))
        sys.stdout.flush()


    def notice(self, message, indent=None):
        '''Outputs a notice message.'''
        self.__print_message(message, '+', indent)
        self.process_signals()


    def __pid_lock(self):
        params = []
        params_str = '';
        if self.args is not None:
            for param in list(vars(self.args).values()):
                if param is not None:
                    params.append(str(param).lower())

            params.sort()
            params_str = '_'.join(str(v) for v in params)

        base_name = '/var/run/cli'
        if os.path.isdir(base_name) is False:
            raise CLIException(
                'base directory "' + base_name + '" does not exist')

        base_name += '/' +os.path.basename(sys.argv[0])

        if len(params) > 0:
            base_name += '-' + re.sub('[^A-Za-z0-9_\-]', '', params_str.lower())

        self.__pid_lock_file = base_name + '.pid_lock'

        active_pid = self.__get_active_pid()
        if active_pid is not None:
            try:
                os.kill(int(active_pid), 0)
                self.__pid_lock_failed()
            except OSError:
                os.unlink(self.__pid_lock_file)

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

        sys.stdout.flush()
        sys.exit(0);


    def __print_message(self, message, char, indent=None):
        if indent is not None:
            print((' ' * 4 *indent) + message)
        else:
            print(char + ' ' + message)

        sys.stdout.flush()


    def process_signals(self):
        if self.__stop_on_signal and os.path.isfile(CLI_STOP_SIGNAL_FILE):
            self.__status_id = self.STATUS_ERROR
            self.__print_message('CLI execution has been stopped!', '!')
            self.exit()


    def set_status_error(self):
        self.__status_id = self.STATUS_ERROR


    def sleep(self, num_seconds):
        self.process_signals()
        self.notice('Sleeping (' + str(num_seconds) + ')...')
        time.sleep(num_seconds)
        return self


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
        sys.stdout.flush()


    def time_marker(self, num_iterations=None, max_iterations=None):
        '''Outputs the time for each iteration of a CLI that runs in a loop
           continuously.'''
        self.process_signals()

        if num_iterations and \
           max_iterations and \
           num_iterations > max_iterations:
            self.notice('Exiting to recover resources...')
            self.exit()

        self.notice(
            ('----- Marker '
             + (str(num_iterations) if num_iterations is not None else '')
             + ' ['
             + str(datetime.datetime.now())
             + ']'))

        return num_iterations + 1


    def warn(self, message, indent=None):
        '''Outputs a warning message.'''
        self.__print_message(message, '*', indent)
        self.process_signals()


class CLIOutputRenderer(object):
    '''Provides methods for consistent output from CLI programs.'''

    @staticmethod
    def header(title, width=79):
        enclosure = '# +' + ('-' * (width - 5)) + "+\n"
        body = '# | ' + title
        body += ' ' * (width - 2 - len(body)) + "|\n"

        return enclosure + body + enclosure

# ----- Private Functions  ----------------------------------------------------

def _handle_cli_exception_logging(e):
    log_file = ConfigManager().value('cli log file')
    if log_file:
        logging.basicConfig(filename = log_file)
        logging.critical(traceback.format_exc())
        logging.shutdown()
