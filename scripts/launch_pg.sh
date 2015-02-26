#!/bin/bash

NAME=db1
IMAGE=ndslabs/postgres-icat

docker pull $IMAGE
( docker rm -f $NAME > /dev/null ; true )
docker run \
   -d \
   --env-file=/etc/hubenv \
   -v /mnt/data/volumes/pg/icat:/var/lib/postgresql/data \
   --name $NAME $IMAGE

NAME=db2
IMAGE=ndslabs/postgres-owncloud
( docker rm -f $NAME > /dev/null ; true )
docker run \
   -d \
   --env-file=/etc/hubenv \
   -v /mnt/data/volumes/pg/owncloud:/var/lib/postgresql/data \
   --name $NAME $IMAGE
