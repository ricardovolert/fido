FROM debian:sid

RUN apt-get update && \
  apt-get install -qy python-flask ssh-client && \
  rm -rf /var/lib/apt/lists/*

RUN groupadd -g 1000 fido && \
  useradd -m -g 1000 -G 1000 -u 1000 -s /bin/bash fido

WORKDIR /home/fido

ADD server.py /home/fido/server.py
ADD sshdir /home/fido/.ssh

RUN ssh-keyscan -H dickenson.dreamhost.com > /home/fido/.ssh/known_hosts
RUN chown fido:fido -R /home/fido

EXPOSE 5000
USER fido
CMD python /home/fido/server.py
