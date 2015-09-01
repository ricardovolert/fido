FROM ubuntu:trusty

RUN apt-get update -qy && \
  apt-get install -qy python-minimal python-setuptools curl git python-jinja2 \
    python-werkzeug python-pygments python-simplejson python-babel python-pillow \
    python-sqlalchemy unzip python-mysqldb && \
  apt-get clean && \
  rm -rf /var/lib/apt/lists/*

RUN cd /tmp && \
  curl -LO https://github.com/openstack-infra/lodgeit/archive/master.zip && \
  unzip master.zip && \
  rm -rf /tmp/lodgeit-master/manage.py

ADD manage.py /tmp/lodgeit-master/manage.py

WORKDIR /tmp/lodgeit-master
EXPOSE 5000
CMD ["python", "manage.py", "runserver", "-h", "0.0.0.0", "-p", "5000"]
