FROM centos:6

RUN yum update -q -y && \
  yum install -y wget gcc gcc-c++ bzip2 openssh-server && \
  cd /tmp && \
  wget --no-cookies --no-check-certificate \
    --header "Cookie: gpw_e24=http%3A%2F%2Fwww.oracle.com%2F; oraclelicense=accept-securebackup-cookie" \
    "http://download.oracle.com/otn-pub/java/jdk/8u71-b15/jdk-8u71-linux-x64.rpm" && \
  rpm -i jdk-8u71-linux-x64.rpm* && rm -rf jdk* && \
  sed -ri 's/^session\s+required\s+pam_loginuid.so$/session optional pam_loginuid.so/' /etc/pam.d/sshd && \
  adduser fido 

RUN mkdir -p /var/log/supervisor

USER fido
WORKDIR /home/fido

RUN wget -q https://repo.continuum.io/miniconda/Miniconda-latest-Linux-x86_64.sh && \
  bash Miniconda-latest-Linux-x86_64.sh -bf && \
  echo 'export PATH=/home/fido/miniconda2/bin:$PATH' >> /home/fido/.bashrc && \
  miniconda2/bin/conda update -q -y --prefix /home/fido/miniconda2 conda && \
  miniconda2/bin/conda install -q -y conda-build anaconda-client git mercurial supervisor && \
  rm -rf Miniconda-latest-Linux-x86_64.sh 

USER root

COPY sshd.conf /etc/supervisor/conf.d/sshd.conf
COPY supervisord.conf /etc/

EXPOSE 22

CMD ["/home/fido/miniconda2/bin/supervisord", "-n"]
