FROM ubuntu:precise

ADD ./bootstrap.sh /tmp/bootstrap.sh
RUN bash /tmp/bootstrap.sh

ADD ./supervisord.conf /etc/supervisord.conf
ADD ./modelconvert.conf /etc/supervisor.d/modelconvert.conf
ADD ./run.sh /usr/local/bin/run.sh

RUN chmod +x /usr/local/bin/run.sh && mkdir -p /var/log/supervisor

EXPOSE 5001

CMD supervisord -n -c /etc/supervisord.conf
