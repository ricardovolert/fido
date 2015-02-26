#!/bin/bash

NAME=proxy
IMAGE=ndslabs/proxy

docker pull $IMAGE
( docker rm -f $NAME > /dev/null ; true )
docker run \
   -d \
   -p 8088:8000 \
   -p 8001 \
   --env-file=/etc/hubenv \
   --name $NAME \
   $IMAGE
