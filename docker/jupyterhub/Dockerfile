FROM jupyter/jupyterhub

ENV BITBUCKET_CLIENT_ID=github_id BITBUCKET_CLIENT_SECRET=github_secret \
  OAUTH_CALLBACK_URL=https://example.com/hub/oauth_callback \
  CONFIGPROXY_AUTH_TOKEN=super-secret DOCKER_HOST=tcp://141.142.234.27:2375

VOLUME ["/srv/jupyterhub/ssl", "/var/run/jupyterhub"]
EXPOSE 443

RUN apt-get install -y libpq-dev mercurial

RUN pip3 install docker-py==1.2.3
RUN pip3 install git+git://github.com/jupyter/dockerspawner.git
RUN pip3 install git+git://github.com/jupyter/oauthenticator.git
RUN pip3 install hg+https://bitbucket.org/MatthewTurk/ythubspawner

# set working directory to the jupyterhub directory
WORKDIR /srv/jupyterhub
