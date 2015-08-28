#!/bin/bash

NAME=ytwebsite_deploy
IMAGE=hub.yt/yt/webdeploy

docker pull $IMAGE
( docker rm -f $NAME > /dev/null ; true )
docker run \
   -d \
   -p 5004:5000 \
   --name $NAME $IMAGE
