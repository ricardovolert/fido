Setting up Docker Swarm
-----------------------

    source ~/dxl-openrc.sh  # download env setup from openstack
    export SWARM_TOKEN=$(docker -H :2375 run swarm create)

    docker-machine create \
      --driver openstack \
      --openstack-ssh-user ubuntu \
      --openstack-sec-groups "remote SSH,default,swarm,jupyterhub" \
      --openstack-flavor-name m1.small \
      --openstack-floatingip-pool "ext-net" \
      --openstack-image-id 9eac331d-46b6-4de8-b7c4-14b8bd9c7214 \ 
      --swarm --swarm-master \
      --swarm-discovery token://$SWARM_TOKEN swarm-master

    docker-machine create \
      --driver openstack \
      --openstack-ssh-user ubuntu \
      --openstack-sec-groups "remote SSH,default,swarm,Docker" \
      --openstack-flavor-name m1.large \
      --openstack-floatingip-pool "ext-net" \
      --openstack-image-id 9eac331d-46b6-4de8-b7c4-14b8bd9c7214 \ 
      --swarm --swarm-discovery token://$SWARM_TOKEN \
      swarm-node-01

    docker-machine create \
      --driver openstack \
      --openstack-ssh-user ubuntu \
      --openstack-sec-groups "remote SSH,default,swarm,Docker" \
      --openstack-flavor-name m1.large \
      --openstack-floatingip-pool "ext-net" \
      --openstack-image-id 9eac331d-46b6-4de8-b7c4-14b8bd9c7214 \ 
      --swarm --swarm-discovery token://$SWARM_TOKEN \
      swarm-node-02

Setting up JupyterHub
---------------------

    ./gencert jupyter.hub.yt  # generate self-signed cert, may require tweaking

    eval $(docker-machine env --swarm swarm-master)
    docker pull jupyter/singleuser
    docker-machine scp -r $DOCKER_CERT_PATH swarm-master:swarm

    # you need to add bb oauth credentials: 
    # OAUTH_CALLBACK_URL BITBUCKET_CLIENT_ID BITBUCKET_CLIENT_SECRET
    env | grep DOCKER_HOST >> jupyterhub.env
    echo CONFIGPROXY_AUTH_TOKEN=$(head -c 30 /dev/urandom | xxd -p) >> jupyterhub.env
    echo DOCKER_CERT_PATH=/etc/swarm >> jupyterhub.env

    eval $(docker-machine env swarm-master)  # head node
    docker-compose build jupyterhub
    docker-compose up -d
