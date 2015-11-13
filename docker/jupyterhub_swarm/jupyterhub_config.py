# jupyterhub_config.py
c = get_config()

import os
pjoin = os.path.join

runtime_dir = os.path.join('/srv/jupyterhub')

# https on :443
c.JupyterHub.ip = '0.0.0.0'
c.JupyterHub.port = 443
c.JupyterHub.ssl_key = '/etc/ssl/private/jupyter.hub.yt.key'
c.JupyterHub.ssl_cert = '/etc/ssl/certs/jupyter.hub.yt.cert'

# spawn with Docker
c.JupyterHub.spawner_class = 'dockerspawner.SwarmSpawner'

# put the JupyterHub cookie secret and state db
# in /var/run/jupyterhub
c.JupyterHub.cookie_secret_file = pjoin(runtime_dir, 'cookie_secret')
c.JupyterHub.db_url = pjoin(runtime_dir, 'jupyterhub.sqlite')
c.JupyterHub.log_file = '/var/log/jupyterhub.log'

# use GitHub OAuthenticator for local users
c.JupyterHub.authenticator_class = 'oauthenticator.BitbucketOAuthenticator'
c.BitbucketOAuthenticator.oauth_callback_url = os.environ['OAUTH_CALLBACK_URL']
c.BitbucketOAuthenticator.client_id = os.environ['BITBUCKET_CLIENT_ID']
c.BitbucketOAuthenticator.client_secret = os.environ['BITBUCKET_CLIENT_SECRET']
# c.BitbucketOAuthenticator.team_whitelist = {'yt_analysis'}

# specify users and admin
#c.Authenticator.whitelist = {'xarthisius'}
c.Authenticator.admin_users = {'xarthisius'}

# The location of jupyterhub data files (e.g. /usr/local/share/jupyter/hub)
c.JupyterHub.data_files_path = '/usr/local/share/jupyter/hub'

c.JupyterHub.hub_ip = '0.0.0.0'
from jupyter_client.localinterfaces import public_ips
from urllib.parse import urlparse
pubip = urlparse(os.environ.get("DOCKER_HOST")).netloc.rsplit(':')[0]
c.Spawner.hub_ip_connect = pubip
c.Spawner.container_prefix = "jupyter"
c.Spawner.container_ip = '0.0.0.0'
c.Spawner.use_docker_client_env = True
c.Spawner.tls_assert_hostname = False
c.Spawner.remove_containers = False
