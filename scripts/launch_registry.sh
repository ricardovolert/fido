#!/bin/bash

NAME=registry
IMAGE=registry:latest

docker pull $IMAGE
( docker rm -f $NAME > /dev/null ; true )
docker run \
   -d \
   -v /mnt/data/volumes/registry:/tmp/registry \
   -e SEARCH_BACKEND=sqlalchemy \
   -e SETTINGS_FLAVOR=local \
   --name $NAME $IMAGE
