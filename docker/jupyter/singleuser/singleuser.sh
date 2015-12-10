#!/bin/sh

usermod -u $LDAP_UID jovyan
echo "/home/jovyan/work ${JPY_USER} ${TOTP_TOKEN}" > /home/jovyan/.davfs2/secrets
chown -R jovyan:users /home/jovyan
sudo -E -H -n -u jovyan mount /home/jovyan/work
sudo -E -H -n -u jovyan \
   PATH=/opt/conda/bin:$PATH jupyterhub-singleuser \
      --port=8888 \
      --ip=0.0.0.0 \
      --user=$JPY_USER \
      --cookie-name=$JPY_COOKIE_NAME \
      --base-url=$JPY_BASE_URL \
      --hub-prefix=$JPY_HUB_PREFIX \
      --hub-api-url=$JPY_HUB_API_URL
