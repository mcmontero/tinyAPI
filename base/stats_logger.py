# ----- Info ------------------------------------------------------------------

__author__ = 'Michael Montero <mcmontero@gmail.com>'

# ----- Imports ---------------------------------------------------------------

from tinyAPI.base.config import ConfigManager

import logging
import random
import tinyAPI

__all__ = [
    'StatsLogger'
]

# ----- Public Classes --------------------------------------------------------

class StatsLogger(object):
    '''Manages writing statistics to the application log file.'''

    def hit_ratio(self, name, requests, hits, pid=None):
        if tinyAPI.env_unit_test() is False and \
           tinyAPI.env_cli() is False and \
           random.randint(1, 100000) == 1:
            log_file = ConfigManager.value('app log file')
            if log_file is not None:
                try:
                    hit_ratio = str((hits / requests) * 100) + '%'
                except ZeroDivisionError:
                    hit_ratio = 'NA'

                lines = [
                    '\n----- ' + name + ' (start) -----'
                ]

                if pid is not None:
                    lines.append('PID #{}'.format(pid))

                lines.extend([
                    'Requests: ' + '{0:,}'.format(requests),
                    'Hits: ' + '{0:,}'.format(hits),
                    'Hit Ratio: ' + hit_ratio,
                    '----- ' + name + ' (stop) ------'
                ])

                logging.basicConfig(filename = log_file)
                logging.critical('\n'.join(lines))
                logging.shutdown()
