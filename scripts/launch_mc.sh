#!/bin/bash

NAME=modelconvert
IMAGE=xarthisius/modelconvert:latest

docker pull $IMAGE
( docker rm -f $NAME > /dev/null ; true )
docker run \
   -d \
   -p 5001:5001 \
   -v /mnt/data/volumes/modelconvert/uploads:/tmp/uploads \
   -v /mnt/data/volumes/modelconvert/downloads:/tmp/downloads \
   --env-file=/etc/modelconvert.env \
   --name $NAME \
   $IMAGE
