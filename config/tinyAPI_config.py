''' tinyAPI_config.py -- The configuration file for tinyAPI.'''

# ----- Configuration ---------------------------------------------------------

values = {

    ##
    # Defines the underlying data store into which all entities are stored.
    #
    # Supported values include:
    #
    #   mysql
    #       configure "mysql connection data" below
    ##
    'data store': 'mysql',

    ##
    # An array of Memcached servers to use for caching.  The array should be
    # in the following format:
    #
    #   ['IP Address 1':Port 1],
    #   ['IP Address 2':Port 2],
    #   ...
    #   ['IP Address N':Port N]
    ##
    'memcached servers': ['127.0.0.1:11211']
}
