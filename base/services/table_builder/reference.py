'''reference.py -- Short cut for interacting with reference data.'''

__author__ = 'Michael Montero <mcmontero@gmail.com>'

# ----- Imports ---------------------------------------------------------------

import builtins
from tinyAPI.base.config import ConfigManager

# ----- Public Functions  -----------------------------------------------------

def refv(ref_table_name, value=None):
    '''To use this function, pass in the following sets of parameters:

        * ref_table_name : the name of the reference table
          value          : None
            This will return a dictionary representing the entire reference
            table.

        * ref_table_name : the name of the reference table
          value          : integer ID
            Decodes the integer ID into the string reference value.

        * ref_table_name : the name of the reference table
          value          : string reference value
            Encodes the string reference value into the ID.'''

    if ConfigManager.value('reference definition file') is None:
        return None

    func = getattr(builtins, '_' + ref_table_name.lower())
    table = func()

    if value is None:
        return table

    value_is_id = True
    try:
        int(value)
    except ValueError:
        value_is_id = False

    if value_is_id is False:
        # Flip the keys and values so we can get the ID from the string.
        table = dict((v, k) for k, v in table.items())

    try:
        return table[value]
    except KeyError:
        return None
