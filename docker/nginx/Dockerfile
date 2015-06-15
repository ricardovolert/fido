FROM debian:sid

# Install Supervisor.
RUN \
  apt-get update && \
  apt-get install -y supervisor && \
  rm -rf /var/lib/apt/lists/* && \
  sed -i 's/^\(\[supervisord\]\)$/\1\nnodaemon=true/' /etc/supervisor/supervisord.conf

# Install nginx
RUN \
  apt-get update && \
  apt-get install -y nginx && \
  rm -rf /var/lib/apt/lists/* && \
  echo "\ndaemon off;" >> /etc/nginx/nginx.conf && \
  chown -R www-data:www-data /var/lib/nginx

# Install python-etcd
RUN \
  apt-get update && \
  apt-get install -y python-urllib3 python-openssl wget python-setuptools && \
  cd /tmp && \
  wget https://pypi.python.org/packages/source/p/python-etcd/python-etcd-0.3.3.tar.gz && \
  tar xvf python-etcd-*.tar.gz && cd python-etcd-* && python setup.py install && \
  apt-get -qy remove wget && \
  rm -rf /var/lib/apt/lists/* /tmp/python-etcd*

ADD ./root.tgz /

VOLUME ["/etc/nginx/certs"]
CMD ["supervisord", "-n", "-c", "/etc/supervisor/supervisord.conf"]
