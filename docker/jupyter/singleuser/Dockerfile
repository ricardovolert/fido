FROM jupyter/scipy-notebook:4.0

MAINTAINER Data Exploration Lab <dxl@ncsa.illinois.edu>

ENV TINI_VERSION v0.6.0
ADD https://github.com/krallin/tini/releases/download/${TINI_VERSION}/tini /usr/bin/tini
RUN chmod +x /usr/bin/tini
ENTRYPOINT ["/usr/bin/tini", "--"]

RUN DEBIAN_FRONTEND=noninteractive apt-get install -qyy curl libxml2-dev libz-dev libneon27-gnutls-dev && \
  groupadd davfs2 && \
  cd /tmp && \
  curl -OJ http://mirror.lihnidos.org/GNU/savannah/davfs2/davfs2-1.5.2.tar.gz && \
  tar xf davfs2-1.5.2.tar.gz && \
  cd davfs2-1.5.2 && \
  ./configure dav_user=nobody --enable-largefile --prefix=/usr \
    --mandir=/usr/share/man --infodir=/usr/share/info --datadir=/usr/share --sysconfdir=/etc --localstatedir=/var/lib && \
  make && make install && \
  mkdir /var/run/mount.davfs && \
  chown root:davfs2 /var/run/mount.davfs && \
  chmod 1774 /var/run/mount.davfs && \
  chmod 4755 /usr/sbin/mount.davfs && \
  cd /tmp && rm -rf davfs2*

ADD davfs2.conf /etc/davfs2/davfs2.conf
ADD fido.pem /etc/davfs2/certs/fido.pem
RUN echo "https://hub.yt/owncloud/remote.php/webdav /home/jovyan/work davfs user,rw,noauto 0 0" >> /etc/fstab && \
  usermod -aG davfs2 jovyan && \
  mkdir /home/jovyan/.davfs2 && \
  touch /home/jovyan/.davfs2/secrets && \
  chown jovyan:users /home/jovyan/.davfs2/secrets && \
  chmod 600 /home/jovyan/.davfs2/secrets && \
  chown -R jovyan:users /home/jovyan/.davfs2 /home/jovyan/work && \
  echo "n_cookies 100\nuse_locks 0" >> /home/jovyan/.davfs2/davfs2.conf && \
  chmod 644 /home/jovyan/.davfs2/davfs2.conf && \
  chmod 644 /etc/davfs2/certs/fido.pem

RUN mkdir -p /home/jovyan/.config/matplotlib/ && \
  cp /opt/conda/lib/python3.4/site-packages/matplotlib/mpl-data/matplotlibrc \
     /home/jovyan/.config/matplotlib/ && \
  chown jovyan /home/jovyan/.config/matplotlib/ && \
  sed -i /home/jovyan/.config/matplotlib/matplotlibrc \
      -e '/^backend/ s/Qt4Agg/Agg/'

ADD ./yt_config /home/jovyan/.yt/config

EXPOSE 8888
USER jovyan

RUN conda install -qy h5py numexpr python setuptools numpy sphinx cython \
  nose conda-build sympy
RUN cd /tmp && curl -JO https://bitbucket.org/yt_analysis/yt/get/yt.tar.bz2 && \
  tar xvf yt*.tar.bz2 && cd yt_analysis* && \
  python setup.py install && cd /tmp && rm -rf yt*
RUN pip install galanyl

ADD https://raw.githubusercontent.com/jupyter/jupyterhub/master/jupyterhub/singleuser.py /usr/local/bin/jupyterhub-singleuser
RUN chmod 755 /usr/local/bin/jupyterhub-singleuser

ADD singleuser.sh /srv/singleuser/singleuser.sh
CMD ["sh", "/srv/singleuser/singleuser.sh"]