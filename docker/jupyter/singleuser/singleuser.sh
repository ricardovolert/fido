#!/bin/sh

( echo "$JPY_USER\n$TOTP_TOKEN\nY\n" | mount /home/jovyan/work )

jupyterhub-singleuser \
  --port=8888 \
  --ip=0.0.0.0 \
  --user=$JPY_USER \
  --cookie-name=$JPY_COOKIE_NAME \
  --base-url=$JPY_BASE_URL \
  --hub-prefix=$JPY_HUB_PREFIX \
  --hub-api-url=$JPY_HUB_API_URL
