#!/bin/bash

NAME=jupyterhub-dev
IMAGE=hub.yt/jupyter/jupyterhub:latest
DATA=/mnt/data/volumes/jupyterhub

docker pull $IMAGE
( docker rm -f $NAME > /dev/null ; true )

docker run \
   -d \
   -h $NAME \
   -p 8434:443 \
   --env-file=$DATA/env.dev \
   -v $DATA/ssl:/srv/jupyterhub/ssl \
   -v $DATA/state-dev:/var/run/jupyterhub \
   --link db2:ocdbhost \
   --name $NAME $IMAGE
