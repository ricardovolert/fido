FROM jupyter/scipy-notebook:latest

MAINTAINER Data Exploration Lab <dxl@ncsa.illinois.edu>

ENV TINI_VERSION v0.6.0
ADD https://github.com/krallin/tini/releases/download/${TINI_VERSION}/tini /usr/bin/tini
RUN chmod +x /usr/bin/tini
ENTRYPOINT ["/usr/bin/tini", "--"]

RUN DEBIAN_FRONTEND=noninteractive apt-get install -qyy curl sudo julia libxml2-dev libz-dev libneon27-gnutls-dev && \
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

RUN cd /tmp && \
  apt-get install -qy cmake libxi-dev libtbb-dev libice-dev libopenexr-dev imagemagick freeglut3-dev libxmu-dev && \
  git clone https://github.com/embree/embree.git embree && \
  cd embree && \
  git checkout v2.6.1 && \
  mkdir build && \
  cd build && \
  cmake .. -DENABLE_ISPC_SUPPORT=OFF -DCMAKE_INSTALL_PREFIX=/usr && \
  make -j4 && make install && \
  ln -s /usr/lib/libembree.so.2.6.1 /usr/lib/libembree.so && \
  cd /tmp && rm -rf embree

EXPOSE 8888
USER jovyan

COPY ./envs /tmp/
COPY kernels.sh /tmp/kernels.sh
RUN conda install -qy ipython conda-build yt
RUN chmod +x /tmp/kernels.sh && /tmp/kernels.sh
ADD https://raw.githubusercontent.com/jupyter/jupyterhub/master/jupyterhub/singleuser.py /usr/local/bin/jupyterhub-singleuser
RUN chmod 755 /usr/local/bin/jupyterhub-singleuser
RUN julia -e 'Pkg.add("IJulia"); Pkg.add("YT");'

ADD singleuser.sh /srv/singleuser/singleuser.sh
USER root
CMD ["sh", "/srv/singleuser/singleuser.sh"]
