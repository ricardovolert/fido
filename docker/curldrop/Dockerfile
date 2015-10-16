FROM ubuntu:trusty
MAINTAINER xarthisius.kk@gmail.com
RUN locale-gen en_US.UTF-8
ENV LANG=en_US.UTF-8 LANGUAGE=en_US.UTF-8 LC_ALL=en_US.UTF-8 \
  PYTHONPATH=/usr/local/lib/python2.7/dist-packages \
  DEBIAN_FRONTEND=noninteractive BASEURL=http://example.com/ \
  UPLOADDIR=/mnt/uploads

RUN apt-get update -qy && \
  apt-get install -qy wget sudo unzip \
    krb5-locales libasn1-8-heimdal libcurl3-gnutls libgssapi-krb5-2 \
    libgssapi3-heimdal libhcrypto4-heimdal libheimbase1-heimdal \
    libheimntlm0-heimdal libhx509-5-heimdal libk5crypto3 libkeyutils1 \
    libkrb5-26-heimdal libkrb5-3 libkrb5support0 libldap-2.4-2 libmysqlclient18 \
    libpython-stdlib libpython2.7-minimal libpython2.7-stdlib libroken18-heimdal \
    librtmp0 libsasl2-2 libsasl2-modules libsasl2-modules-db libwind0-heimdal \
    mysql-common python python-minimal python-mysqldb python-pycurl \
    python2.7 python2.7-minimal python-werkzeug supervisor && \ 
    apt-get clean && rm -rf /var/lib/apt/lists/*

RUN cd /tmp && wget --quiet https://github.com/nephics/tornado/archive/streambody.zip && \
  unzip -qq streambody.zip && cd tornado-streambody/ && \
  python setup.py install && rm -rf  /tmp/*streambody*

RUN cd /tmp && wget --quiet https://github.com/Xarthisius/curldrop/archive/master.zip && \
  unzip -qq master.zip

VOLUME ["/mnt/uploads"]
EXPOSE 8888

ADD supervisord.conf /etc/supervisor/supervisord.conf
ADD curldrop.conf /etc/supervisor/conf.d/curldrop.conf

CMD ["supervisord", "-n", "-c", "/etc/supervisor/supervisord.conf"]
