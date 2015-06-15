FROM debian:sid

RUN apt-get -qy update && \
   apt-get -qyy install unzip curl python-pip mercurial python-hglib && \
   apt-get clean && \
   rm -rf /var/lib/apt/lists/*

RUN cd /tmp && \
   curl -O https://codeload.github.com/Xarthisius/python-rtmbot/zip/master && \
   unzip master && \
   cd python-rtmbot-master && \
   pip install -r requirements.txt

ADD ./bb.py /tmp/python-rtmbot-master/plugins/bb.py
ADD ./hgbb.py /tmp/python-rtmbot-master/plugins/hgbb.py
ADD ./rtmbot.conf /tmp/python-rtmbot-master/rtmbot.conf

WORKDIR /tmp/python-rtmbot-master
CMD ["python", "rtmbot.py"]
