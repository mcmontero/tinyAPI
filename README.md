The Python tiny api Project - Copyright 2014 Michael C. Montero (mcmontero@gmail.com)

GOALS
=====

    Primary
    -------
      * To provide a minimalist framework for developing REST based API's in
        Python.
      * To automate as much functionality as possible for handling data
        interactions from the API end point to the data store.

    Secondary
    ---------
        * To completely abstract away the data store layer and make switching
          between data stores seamless.
        * To abstract SQL to an intermediate, minimal "language".
        * To automate the building of RDBMS objects.

PYTHON CONFIGURATION
====================

    - pip3 install pycrypto

    - pip3 install --allow-external mysql-connector-python \
                mysql-connector-python

    - pip3 install python3-memcached

    - Create a module called

        tinyAPI_config.py

    - Create it with the default values found in the documentation version of
      this file here:

        conf/tinyAPI_config.py

    - Customize it for your project.

    - Add the path to where tinyAPI is stored and the path to the configuration
      file to the environment variable PYTHONPATH.  If tinyAPI is deployed in
      /opt/tinyAPI and the configuration file is located at
      /opt/my_application/config, make sure your environment contains the
      following:

        export PYTHONPATH=$PYTHONPATH:/opt:/opt/my_application/config
