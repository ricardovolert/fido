FROM debian:sid

RUN apt-get -qqy update && \
  apt-get install -qqy python3-tornado && \
  apt-get clean && \ 
  rm -rf /var/lib/apt/lists/*

ADD ./server.py /tmp/server.py
EXPOSE 80
CMD ["python3", "/tmp/server.py"]
