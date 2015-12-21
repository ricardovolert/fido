FROM jupyter/scipy-notebook:4.0

MAINTAINER Data Exploration Lab <dxl@ncsa.illinois.edu>

ENV TINI_VERSION v0.6.0
ADD https://github.com/krallin/tini/releases/download/${TINI_VERSION}/tini /usr/bin/tini
RUN chmod +x /usr/bin/tini
ENTRYPOINT ["/usr/bin/tini", "--"]

#sed -e "/open_browser/a c.NotebookApp.base_url = '/galaxy-demo/'\nc.NotebookApp.webapp_settings = {'static_url_prefix':'/galaxy-demo/static/'}" \
#   -i /home/jovyan/.jupyter/jupyter_notebook_config.py && \
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

EXPOSE 8888
USER jovyan

RUN conda install -qy h5py numexpr yt
RUN pip install galanyl

ADD singleuser.sh /srv/singleuser/singleuser.sh
CMD ["sh", "/srv/singleuser/singleuser.sh"]
