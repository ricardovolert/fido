FROM jupyter/minimal-notebook:latest

MAINTAINER Data Exploration Lab <dxl@ncsa.illinois.edu>

USER root
COPY ./envs /tmp/
COPY kernels.sh /tmp/kernels.sh
RUN chmod +x /tmp/kernels.sh

USER jovyan
RUN /tmp/kernels.sh
ADD ./logo.png /home/jovyan/.jupyter/custom/logo.png
ADD ./custom.css /home/jovyan/.jupyter/custom/custom.css
