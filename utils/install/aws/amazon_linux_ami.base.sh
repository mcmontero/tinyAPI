#!/bin/bash

/bin/echo "Installing OS packages..."
/usr/bin/yum -y install zlib-devel
/usr/bin/yum -y install gcc
/usr/bin/yum -y install gcc-c++
/usr/bin/yum -y install python-devel
/usr/bin/yum -y install openssl-devel
/usr/bin/yum -y install bzip2-devel
/usr/bin/yum -y install pcre
/usr/bin/yum -y install pcre-devel
/usr/bin/yum -y install mysql-server
/usr/bin/yum -y install mysql
/usr/bin/yum -y install memcached
/usr/bin/yum -y install libmemcached
/usr/bin/yum -y install libmemcached-devel
/usr/bin/yum -y install ImageMagick
/usr/bin/yum -y install python-magic
/usr/bin/yum -y install mailx
/usr/bin/yum -y install postfix
/usr/bin/yum -y install pam-devel
/usr/bin/yum -y install telnet

/bin/echo "Replacing sendmail with postfix..."
/bin/rpm -e sendmail

/bin/echo "Installing Python 3.5.0..."
(cd $HOME; \
 /usr/bin/wget https://www.python.org/ftp/python/3.5.0/Python-3.5.0.tar.xz; \
 /usr/bin/xz -d ./Python-3.5.0.tar.xz; \
 /bin/tar xvf ./Python-3.5.0.tar; \
 cd ./Python-3.5.0; \
 ./configure --prefix=/usr/local; \
 /usr/bin/make; \
 /usr/bin/make altinstall; \
 cd $HOME;
 /bin/rm -rf ./Python-3.5.0*)
/bin/ln -sf /usr/local/bin/python3.5 /usr/bin/python3
/bin/ln -sf /usr/local/bin/pip3.5 /usr/bin/pip3

/bin/echo "Installing Python packages..."
/usr/bin/yes | /usr/bin/pip3 install uwsgi
/usr/bin/yes | /usr/bin/pip3 install pymysql
/usr/bin/yes | /usr/bin/pip3 install python3-memcached
/usr/bin/yes | /usr/bin/pip3 install flask
/usr/bin/yes | /usr/bin/pip3 install flask-restful
/usr/bin/yes | /usr/bin/pip3 install passlib
/usr/bin/yes | /usr/bin/pip3 install python-magic
/usr/bin/yes | /usr/bin/pip3 install pycrypto
/usr/bin/yes | /usr/bin/pip3 install requests
/usr/bin/yes | /usr/bin/pip3 install twilio
/usr/bin/yes | /usr/bin/pip3 install geopy
/usr/bin/yes | /usr/bin/pip3 install pylibmc
/usr/bin/yes | /usr/bin/pip3 install mock
/usr/bin/yes | /usr/bin/pip3 install phonenumbers

/bin/echo "Upgrading pip 2..."
/usr/local/bin/pip install --upgrade pip

/bin/echo "Installing s3cmd..."
(cd $HOME; \
 /usr/bin/wget \
    http://sourceforge.net/projects/s3tools/files/latest/download?source=files \
    -O s3cmd.tar.gz; \
 /bin/gunzip s3cmd.tar.gz; \
 /bin/mkdir ./s3cmd; \
 /bin/tar xvf s3cmd.tar -C ./s3cmd --strip-components=1; \
 cd s3cmd; \
 /usr/bin/python setup.py install; \
 cd $HOME; \
 /bin/rm -rf s3cmd*; \
 /bin/ln -sf /usr/local/bin/s3cmd /usr/bin/s3cmd)

/bin/echo "Installing Google Authenticator..."
(cd $HOME; \
 /usr/bin/wget \
    https://google-authenticator.googlecode.com/files/libpam-google-authenticator-1.0-source.tar.bz2 \
    -O googleauth.tar.bz2; \
 /usr/bin/bunzip2 googleauth.tar.bz2; \
 /bin/mkdir googleauth; \
 /bin/tar xvf ./googleauth.tar -C ./googleauth  --strip-components=1; \
 cd ./googleauth; \
 /usr/bin/make; \
 /usr/bin/make install;
 cd $HOME; \
 /bin/rm -rf googleauth*)
/bin/echo "auth       required     pam_google_authenticator.so" >> \
    /etc/pam.d/sshd

/bin/echo ""
/bin/echo '!! ACTION REQUIRED !!'
/bin/echo ""
/bin/echo '+ Set "ChallengeResponseAuthentication yes" in /etc/ssh/sshd_config'
/bin/echo '+ /etc/init.d/sshd restart'
/bin/echo '+ /sbin/chkconfig memcached on'
/bin/echo '+ /sbin/chkconfig mysqld on'
