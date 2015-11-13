FROM jupyter/jupyterhub

ENV BITBUCKET_CLIENT_ID=github_id BITBUCKET_CLIENT_SECRET=github_secret \
  OAUTH_CALLBACK_URL=https://example.com/hub/oauth_callback \
  CONFIGPROXY_AUTH_TOKEN=super-secret DOCKER_HOST=defineme \
  DOCKER_MACHINE_NAME=defineme DOCKER_TLS_VERIFY=1 \
  DOCKER_CERT_PATH=defineme

EXPOSE 443

RUN apt-get install -y supervisor

RUN pip3 install git+git://github.com/Xarthisius/dockerspawner.git@swarm
RUN pip3 install git+git://github.com/jupyter/oauthenticator.git

# set working directory to the jupyterhub directory
WORKDIR /srv/jupyterhub

COPY supervisord.conf /etc/supervisor/supervisord.conf
COPY jupyterhub.conf /etc/supervisor/conf.d/jupyterhub.conf
COPY ./etc /etc

CMD ["supervisord", "-n", "-c", "/etc/supervisor/supervisord.conf"]
