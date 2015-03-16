#!/bin/bash
/usr/bin/Xvfb :99 -screen 0 1024x768x24 &
service redis-server start
service postgresql start

sleep 2
supervisorctl start celery
sleep 1
supervisorctl start web
supervisorctl start smtp 

