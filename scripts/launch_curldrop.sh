#!/bin/bash

NAME=curldrop
IMAGE=ndslabs/curldrop

docker pull $IMAGE
( docker rm -f $NAME > /dev/null ; true )
docker run \
   -d \
   -h curldrop \
   -p 8888 \
   -e UPLOADDIR=/mnt/uploads/ \
   -e BASEURL=http://use.yt/upload/ \
   -e DATABASE=/mnt/uploads/files.db \
   -e SERVERBUFF=17179869184 \
   -v /mnt/data/volumes/curldrop:/mnt/uploads \
   --name $NAME $IMAGE

sleep 2
etcdctl -C 192.168.23.2:4001 rm /proxy/proxies/upload
etcdctl -C 192.168.23.2:4001 set /proxy/proxies/upload \
  http://192.168.23.2:$(docker port $NAME 8888 | cut -f2 -d:)
