FROM jupyter/scipy-notebook:4.0

MAINTAINER Data Exploration Lab <dxl@ncsa.illinois.edu>

ENV TINI_VERSION v0.6.0
ADD https://github.com/krallin/tini/releases/download/${TINI_VERSION}/tini /usr/bin/tini
RUN chmod +x /usr/bin/tini
ENTRYPOINT ["/usr/bin/tini", "--"]
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

RUN mkdir -p /home/jovyan/.config/matplotlib/ && \
  cp /opt/conda/lib/python3.4/site-packages/matplotlib/mpl-data/matplotlibrc \
     /home/jovyan/.config/matplotlib/ && \
  chown jovyan /home/jovyan/.config/matplotlib/ && \
  sed -i /home/jovyan/.config/matplotlib/matplotlibrc \
      -e '/^backend/ s/Qt4Agg/Agg/'

ADD ./yt_config /home/jovyan/.yt/config
ADD ./quickstart.tar /home/jovyan/work/
RUN wget https://bitbucket.org/data-exp-lab/galaxy-demo/raw/tip/galaxy_visualization.ipynb && \ 
  chmod 644 galaxy_visualization.ipynb

ADD https://raw.githubusercontent.com/jupyter/jupyterhub/master/jupyterhub/singleuser.py /usr/local/bin/jupyterhub-singleuser
RUN chmod 755 /usr/local/bin/jupyterhub-singleuser

COPY ./envs /tmp/
COPY kernels.sh /tmp/kernels.sh
RUN chmod +x /tmp/kernels.sh

EXPOSE 8888
USER jovyan

RUN /tmp/kernels.sh

ADD singleuser.sh /srv/singleuser/singleuser.sh
CMD ["sh", "/srv/singleuser/singleuser.sh"]
