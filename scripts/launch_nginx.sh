#!/bin/bash

NAME=nginx
IMAGE=xarthisius/nginx:latest

docker pull $IMAGE
( docker rm -f $NAME > /dev/null ; true )
docker run \
   -d \
   -p 443:443 \
   -p 80:80 \
   --link registry:registry \
   --link prhandler:prhandler \
   --name $NAME \
   -v /root/nginx/nginx:/etc/nginx \
   -v /root/nginx/ssl:/etc/ssl \
   $IMAGE
