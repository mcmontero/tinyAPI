The Python tiny api Project - Copyright 2014 Michael C. Montero (mcmontero@gmail.com)

SUGGESTED STEPS
===============

    Install tinyAPI
    ---------------
        Execute these steps as root
        /usr/bin/yum -y install git
        cd /opt
        mkdir tinyAPI
        cd tinyAPI
        /usr/bin/git clone https://github.com/mcmontero/tinyAPI.git .

    OS/Software Configuration
    -------------------------
        cd /opt/tinyAPI/utils/install
        cd aws
        ./amazon_linux_ami.base.sh
        cd ../nginx
        ./with_headers_more.sh
        cd ../mysqld
        ./with_timezone_data.sh
