#!/bin/bash
source /etc/hubenv

NAME=icat1
IMAGE=ndslabs/irods-icat

docker pull $IMAGE
( docker rm -f $NAME &> /dev/null ; true )
docker run \
   -d \
   --env-file=/etc/hubenv \
   -v /mnt/data/volumes/irods:/var/lib/irods/Vault \
   --link db1:db1 \
   -p 1247 \
   -h $NAME \
   --name $NAME $IMAGE

sleep 3

etcdctl -C 192.168.23.2:4001 set /irods/port $(docker port icat1 1247 | cut -f 2 -d:)
etcdctl -C 192.168.23.2:4001 set /irods/zone ${irodszone}
etcdctl -C 192.168.23.2:4001 set /irods/host ${COREOS_PRIVATE_IPV4}

NAME=irodsrest
IMAGE=ndslabs/irods-rest

docker pull $IMAGE
( docker rm -f $NAME &> /dev/null ; true )
docker run \
   -d \
   --env-file=/etc/hubenv \
   -v /mnt/data/volumes/irods:/mnt/data \
   --link icat1:icat1 \
   -p 80 -p 443 \
   --name $NAME $IMAGE

sleep 3

etcdctl -C 192.168.23.2:4001 set /proxy/proxies/irods-rest http://${COREOS_PRIVATE_IPV4}:$(docker port irodsrest 80 | cut -f2 -d:)

NAME=owncloud1
IMAGE=ndslabs/owncloud:8.0.2
docker pull $IMAGE
( docker rm -f $NAME &> /dev/null ; true )
docker run \
   -d \
   --env-file=/etc/hubenv \
   --link db2:ocdbhost \
   --link irodsrest:irodsrest \
   -p 80 \
   -v /mnt/data/volumes/owncloud/config:/var/www/owncloud/config \
   -v /mnt/data/volumes/owncloud/data:/var/www/owncloud/data \
   --name $NAME $IMAGE

sleep 3

etcdctl -C 192.168.23.2:4001 set /proxy/proxies/owncloud \
  http://${COREOS_PRIVATE_IPV4}:$(docker port owncloud1 80 | cut -f2 -d:)/owncloud
