# ----- Info ------------------------------------------------------------------

__author__ = 'Michael Montero <mcmontero@gmail.com>'

# ----- Imports ---------------------------------------------------------------

import re
import tinyAPI

__all__ = [
    'MySQLIndexUsageParser'
]

# ----- Public Classes --------------------------------------------------------

class MySQLIndexUsageParser(object):
    '''
    Parses the mysqlindexcheck script output and reformats it for the Schema
    Difference tool.
    '''

    def __init__(self):
        self.clustered_indexes = []
        self.redundant_indexes = []


    def execute(self, script_output):
        lines = script_output.decode().split('\n')
        if len(lines) == 0:
            return None

        for i in range(2, len(lines)):
            if re.search(
                'contain(s)? the clustered index',
                lines[i]
            ):
                while True:
                    i += 2
                    if i > len(lines) or \
                       (not re.search('^create ', lines[i].lower()) and
                        not re.search('^alter ', lines[i].lower())):
                        break

                    index = self.__extract_index_details(lines[i])
                    if index is None:
                        raise RuntimeError(
                            'could not extract index details from "{}"'
                                .format(lines[i])
                        )

                    self.clustered_indexes.append([index[0], index[1]])
            elif re.search(
                'The following index is a duplicate or redundant',
                lines[i]
            ):
                i += 2

                index = self.__extract_index_details(lines[i])
                if index is None:
                    raise RuntimeError(
                        'could not extract index details from "{}"'
                            .format(lines[i])
                    )

                i += 2

                duplicate = self.__extract_index_details(lines[i])
                if index is None:
                    raise RuntimeError(
                        'could not extract index details from "{}"'
                            .format(lines[i])
                    )

                self.redundant_indexes.append(
                    [
                        index[0], index[1], duplicate[0], duplicate[1]
                    ]
                )

        return self


    def __extract_index_details(self, line):
        matches = \
            re.search(
                'create( unique)? index `(.*)` on `.*`\.`.*` (\(.*\))',
                line.lower()
            )
        if matches is None:
            matches = \
                re.search(
                    'alter table `.*`\.`(.*)` add primary key (\(.*\))',
                    line.lower()
                )
            if matches is None:
                return None
            else:
                return \
                    matches.group(1) + '_pk', re.sub('`', '', matches.group(2))
        else:
            return \
                matches.group(2), re.sub('`', '', matches.group(3))
