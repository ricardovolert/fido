FROM jupyter/minimal-notebook:latest

MAINTAINER Data Exploration Lab <dxl@ncsa.illinois.edu>

USER root
COPY ./envs /tmp/
COPY kernels.sh /tmp/kernels.sh
RUN chmod +x /tmp/kernels.sh

COPY ./config.tri /home/jovyan/.trident/config.tri
RUN wget http://trident-project.org/data/ion_table/hm2012_hr.h5.gz -O /home/jovyan/.trident/hm2012_hr.h5.gz && \
   gunzip /home/jovyan/.trident/hm2012_hr.h5.gz && chown jovyan -R /home/jovyan/.trident

USER jovyan
RUN /tmp/kernels.sh
ADD ./logo.png /home/jovyan/.jupyter/custom/logo.png
ADD ./custom.css /home/jovyan/.jupyter/custom/custom.css
