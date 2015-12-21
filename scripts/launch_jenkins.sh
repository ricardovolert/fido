#!/bin/bash

NAME=jenkins
IMAGE=jenkins

docker pull $IMAGE
( docker rm -f $NAME > /dev/null ; true )
docker run \
   -d \
   -p 18080:8080 \
   -v /mnt/data/volumes/jenkins:/var/jenkins_home \
   --name $NAME $IMAGE
