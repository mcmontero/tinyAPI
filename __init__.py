# ----- Imports ---------------------------------------------------------------

from .dsh import dsh
from importlib.machinery import SourceFileLoader
from tinyAPI.base.config import ConfigManager
from tinyAPI.base.context import *
from tinyAPI.base.data_store.memcache import Memcache
from tinyAPI.base.data_store.exception import DataStoreDuplicateKeyException
from tinyAPI.base.data_store.provider import DataStoreMySQL
from tinyAPI.base.services.table_builder.mysql import Table, RefTable
from tinyAPI.base.services.table_builder.reference import refv

# ----- Instructions ----------------------------------------------------------

ref_defs_file = ConfigManager.value('reference definition file')
if ref_defs_file is not None:
    loader = SourceFileLoader('reference_definition', ref_defs_file)
    loader.load_module('reference_definition')
