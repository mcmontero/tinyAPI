# ----- Info ------------------------------------------------------------------

__author__ = 'Michael Montero <mcmontero@gmail.com>'

# ----- Imports ---------------------------------------------------------------

import subprocess

__all__ = [
    'find_dirs',
    'find_files'
]

# ----- Public Functions ------------------------------------------------------

def find_dirs(path, pattern=None):
    '''Finds directories starting at the specified path and matching the
       specified pattern.'''
    command = ('/usr/bin/find ' + path + ' -type d'
               + (' -name "' + pattern + '"' if pattern is not None else ''))

    results = subprocess.check_output(command, shell=True).decode()
    if not results:
        return []
    else:
        return results.rstrip().split("\n")


def find_files(path, pattern=None):
    '''Finds files starting at the specified path and matching the specified
       pattern.'''
    command = ('/usr/bin/find ' + path + ' -type f'
               + (' -name "' + pattern + '"' if pattern is not None else ''))

    results = subprocess.check_output(command, shell=True).decode()
    if not results:
        return []
    else:
        return results.rstrip().split("\n")
