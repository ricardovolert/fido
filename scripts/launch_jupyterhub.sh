#!/bin/bash

NAME=jupyterhub
IMAGE=hub.yt/jupyter/jupyterhub:anon
DATA=/mnt/data/volumes/$NAME

docker pull $IMAGE
( docker rm -f $NAME > /dev/null ; true )

docker run \
   -d \
   -h $NAME \
   -p 9433:443 \
   --env-file=$DATA/env \
   -v $DATA/ssl:/srv/jupyterhub/ssl \
   -v $DATA/state:/var/run/jupyterhub \
   --name $NAME $IMAGE
