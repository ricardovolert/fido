#!/bin/bash

NAME=jenkins

( docker rm -f $NAME > /dev/null ; true )
docker run -p 8080:8080 -v /mnt/data/volumes/jenkins:/var/jenkins_home --name $NAME jenkins
