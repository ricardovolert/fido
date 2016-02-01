FROM debian:sid

RUN apt-get -qy update && \
   apt-get -qyy install unzip curl python-requests python-websocket \
     python-daemon python-yaml python-setuptools python-future mercurial python-hglib && \
   apt-get clean && \
   rm -rf /var/lib/apt/lists/*

RUN cd /tmp && \
   curl -LJO https://github.com/slackhq/python-slackclient/archive/master.zip && \
   unzip python-slackclient-master.zip && \
   cd python-slackclient-master && \
   python setup.py install && \
   cd /tmp && rm -rf /tmp/*

RUN cd /tmp && \
  curl -LJO https://github.com/msiemens/tinydb/archive/master.zip && \
  unzip tinydb-master.zip && \
  cd tinydb-master && \
  python setup.py install && \
  cd /tmp && rm -rf /tmp/*

RUN cd /tmp && \
   curl -O https://codeload.github.com/Xarthisius/python-rtmbot/zip/master && \
   unzip master

ADD ./bb.py /tmp/python-rtmbot-master/plugins/bb.py
ADD ./hgbb.py /tmp/python-rtmbot-master/plugins/hgbb.py
ADD ./rtmbot.conf /tmp/python-rtmbot-master/rtmbot.conf

WORKDIR /tmp/python-rtmbot-master
CMD ["python", "rtmbot.py"]
