NAME=owncloud1
IMAGE=hub.yt/jupyter/owncloud:8.0.2
docker pull $IMAGE
( docker rm -f $NAME &> /dev/null ; true )

etcdctl -C 192.168.23.2:4001 rm /proxy/proxies/owncloud

docker run \
   -d \
   --env-file=/etc/hubenv \
   --link db2:ocdbhost \
   -p 16580:80 \
   -p 16581:443 \
   -v /mnt/data/volumes/owncloud/config:/var/www/owncloud/config \
   -v /mnt/data/volumes/owncloud/data:/var/www/owncloud/data \
   --name $NAME $IMAGE

sleep 3

etcdctl -C 192.168.23.2:4001 set /proxy/proxies/owncloud \
  http://${COREOS_PRIVATE_IPV4}:$(docker port owncloud1 80 | cut -f2 -d:)/owncloud

