#!/bin/bash

NAME=prhandler
IMAGE=hub.yt/prhandler:yt

#docker pull $IMAGE
( docker rm -f $NAME > /dev/null ; true )
docker run \
   -d \
   -p 8888 \
   --name $NAME $IMAGE
