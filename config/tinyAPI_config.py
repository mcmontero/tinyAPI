'''tinyAPI_config.py -- The configuration file for tinyAPI.'''

# ----- Configuration ---------------------------------------------------------

values = {

    ##
    # The full path to a log file to which to log application messages
    # specifically being written by tinyAPI.
    ##
    'app log file': None,

    ##
    # Defines in which paths tinyAPI and your application live.
    ##
    'application dirs': ['/opt/tinyAPI'],

    ##
    # The full path to a log file to which to log uncaught exceptions that
    # occur during the execution of a CLI script.  If set to None, no logging
    # will occur.
    ##
    'cli log file': None,

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
    # Defines the data stores accessible to tinyAPI.  The format for this
    # setting is as follows:
    #
    #   'data store config': {
    #       '[server name]': {
    #           '[group 1]': {
    #               'durability': 'randomizer',
    #               'hosts': [
    #                   ['[host 1]', '[username 1]', '[password 1]'],
    #                   ...
    #                   ['[host N]', '[username N]', '[password N]']
    #               ]
    #           },
    #           ...
    #           '[group N]': {
    #               'durability': 'randomizer',
    #               'hosts': [
    #                   ['[host 1]', '[username 1]', '[password 1]'],
    #                   ...
    #                   ['[host N]', '[username N]', '[password N]']
    #               ]
    #           },
    #           'type': '[mysql|postgresql]'
    #       }
    #   }
    #
    # For the sake of simplicity only one "server name" configuration is shown
    # but there is no limit to the number that can be configured.
    #
    # durability:
    #   randomizer      A host is selected from the list at random
    #
    # Fail over is built into all durability algorithms where appropriate.  If
    # the connection to the chosen host fails another will be selected both at
    # the time of initial connection and usage.
    ##
    'data store config': {
        'my server': {
            'read write': {
                'algo': 'randomizer',
                'hosts': [
                    ['host', 'username', 'password']
                ]
            ],
            'type': 'mysql'
        }
    }

    ##
    # tinyAPI comes with various libraries that can install data structures
    # into an RDBMS.  The schema defined here is where the objects will be
    # placed.  If this value is set to None, nothing will be loaded.
    ##
    'default schema': None,

    ##
    # The default data store connection to use when executing unit tests
    # and using the TransactionalDataStoreTestCase.
    ##
    'default unit test connection': None,

    ##
    # Executes the mysqlindexcheck script and reports the output as part of
    # the Schema Difference tool.
    ##
    'index check': {
        'database': 'db_name',
        'path': '/usr/local/bin/mysqlindexcheck',
        'server': '[user]:[password]@[host]'
    },

    ##
    # An array of Memcached servers to use for caching.  The array should be
    # in the following format:
    #
    #   ['IP Address 1':Port 1],
    #   ['IP Address 2':Port 2],
    #   ...
    #   ['IP Address N':Port N]
    ##
    'memcached servers': ['127.0.0.1:11211'],

    ##
    # An array that maps a defined configuration name to the necessary MySQL
    # login credentials so that multiple database servers can be used.  This
    # includes the ability to read from a slave and write to a master or
    # distribute reads over sharded slaves.  Each connection should be
    # formatted as follows:
    #
    #   'Connection Name 1': ['Host 1', 'Username 1', 'Password 1'],
    #   'Connection Name 2': ['Host 2', 'Username 2', 'Passowrd 2'],
    #   ...
    #   'Connection Name N': ['Host N', 'Username N', 'Password N']
    ##
    'mysql connection data': {

        'local': ['', '', '']
    },

    ##
    # A list of schema names that the RDBMS Builder should manage.  If the
    # RDBMS Builder is in use you must provide values here.
    ##
    'rdbms builder schemas': ['local'],

    ##
    # The RDBMS Builder can compile the reference tables create with RefTable()
    # into variables so that no database interactions are required to interact
    # with them.  If this value is None, reference definitions will not be
    # compiled.
    ##
    'reference definition file': None
}
