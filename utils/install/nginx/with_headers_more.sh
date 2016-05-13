#!/bin/bash

/bin/echo "Getting nginx..."
(cd $HOME; \
 /usr/bin/wget \
    http://nginx.org/download/nginx-1.9.15.tar.gz \
    -O ./nginx.tar.gz; \
 /bin/gunzip ./nginx.tar.gz; \
 /bin/mkdir nginx; \
 /bin/tar xvf nginx.tar -C ./nginx --strip-components=1)

/bin/echo "Getting ngx_headers_more..."
(cd $HOME; \
 /usr/bin/wget \
   https://github.com/openresty/headers-more-nginx-module/archive/v0.29.tar.gz \
   -O ./headers_more.tar.gz; \
 /bin/gunzip ./headers_more.tar.gz; \
 /bin/mkdir headers_more; \
 /bin/tar xvf ./headers_more.tar -C ./headers_more --strip-components=1)

/bin/echo "Making nginx..."
(cd $HOME/nginx; \
 ./configure \
    --prefix=/opt/nginx \
    --add-module=../headers_more; \
 /usr/bin/make; \
 /usr/bin/make install;
 cd $HOME; \
 /bin/rm -rf nginx*; \
 /bin/rm -rf headers_more*)

/bin/echo "Installing start script..."
/bin/cp ./init.d/nginx /etc/init.d/nginx
/sbin/chkconfig nginx on
