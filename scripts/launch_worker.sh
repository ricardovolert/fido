#!/bin/bash
source /etc/hubenv

NAME=rabbitmq
IMAGE=hub.yt/ythub/rabbitmq

docker pull $IMAGE
( docker rm -f $NAME &> /dev/null ; true )
docker run \
   -d \
   --env-file=/etc/hubenv \
   -p 5672:5672 -p 15672:15672 \
   --name $NAME $IMAGE

sleep 3

etcdctl -C 192.168.23.2:4001 set /rabbitmq/users/ytfido password
etcdctl -C 192.168.23.2:4001 set /rabbitmq/vhosts/ythub 1
etcdctl -C 192.168.23.2:4001 set /rabbitmq/permissions/ythub/ytfido ".*/.*/.*"

NAME=worker
IMAGE=hub.yt/ythub/worker

docker pull $IMAGE
#docker pull ndslabs/hublaunch
#docker pull ndslabs/devenv
#docker pull ndslabs/rstudio
( docker rm -f $NAME &> /dev/null ; true )
docker run \
   -d \
   --env-file=/etc/hubenv \
   -p 7888:8888 \
   --name $NAME $IMAGE

sleep 3
