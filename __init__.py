# ----- Imports ---------------------------------------------------------------

from .dsh import dsh
from importlib.machinery import SourceFileLoader
from tinyAPI.base.config import ConfigManager
from tinyAPI.base.context import *
from tinyAPI.base.data_store.memcache import Memcache
from tinyAPI.base.data_store.exception import ColumnCannotBeNullException
from tinyAPI.base.data_store.exception import DataStoreDuplicateKeyException
from tinyAPI.base.data_store.MySQL import MySQL
from tinyAPI.base.data_store.provider import DataStoreMySQL
from tinyAPI.base.services.table_builder.mysql import Table, RefTable, View
from tinyAPI.base.services.table_builder.reference import refv

import tinyAPI.base.data_store.ConnectionManager

# ----- Public Functions ------------------------------------------------------

def load_reference_definitions(ref_defs_file):
    if ref_defs_file is not None:
        loader = SourceFileLoader('reference_definition', ref_defs_file)
        loader.load_module('reference_definition')

# ----- Instructions ----------------------------------------------------------

load_reference_definitions(ConfigManager.value('reference definition file'))
