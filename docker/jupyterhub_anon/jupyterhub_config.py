# jupyterhub_config.py
c = get_config()

import os
pjoin = os.path.join

runtime_dir = os.path.join('/srv/jupyterhub')
ssl_dir = pjoin(runtime_dir, 'ssl')
if not os.path.exists(ssl_dir):
    os.makedirs(ssl_dir)


# https on :443
c.JupyterHub.port = 443
c.JupyterHub.ssl_key = pjoin(ssl_dir, 'yt-project_org.key')
c.JupyterHub.ssl_cert = pjoin(ssl_dir, 'yt-project_org.pem')

# spawn with Docker
c.JupyterHub.spawner_class = 'dockerspawner.DockerSpawner'

# The docker instances need access to the Hub, so the default loopback port doesn't work:
#from IPython.utils.localinterfaces import public_ips
from jupyter_client.localinterfaces import public_ips
pubip = public_ips()[0]
c.JupyterHub.hub_ip = pubip

# put the JupyterHub cookie secret and state db
# in /var/run/jupyterhub
c.JupyterHub.cookie_secret_file = pjoin(runtime_dir, 'cookie_secret')
c.JupyterHub.db_url = pjoin(runtime_dir, 'jupyterhub.sqlite')
# or `--db=/path/to/jupyterhub.sqlite` on the command-line

# put the log file in /var/log
c.JupyterHub.log_file = '/var/log/jupyterhub.log'

# use GitHub OAuthenticator for local users

c.JupyterHub.authenticator_class = 'oauthenticator.BitbucketOAuthenticator'
c.BitbucketOAuthenticator.oauth_callback_url = os.environ['OAUTH_CALLBACK_URL']
c.BitbucketOAuthenticator.client_id = os.environ['BITBUCKET_CLIENT_ID']
c.BitbucketOAuthenticator.client_secret = os.environ['BITBUCKET_CLIENT_SECRET']
# c.BitbucketOAuthenticator.team_whitelist = {'yt_analysis'}
# create system users that don't exist yet
# c.LocalAuthenticator.create_system_users = True

# specify users and admin
#c.Authenticator.whitelist = {'xarthisius'}
c.Authenticator.admin_users = {'xarthisius'}

# The location of jupyterhub data files (e.g. /usr/local/share/jupyter/hub)
c.JupyterHub.data_files_path = '/usr/local/share/jupyter/hub'
#c.JupyterHub.base_url = '/%s' % os.environ.get("HUB_PREFIX", "jupyter")
#c.JupyterHub.hub_prefix = '/%s/hub/' % os.environ.get("HUB_PREFIX", "jupyter")

# start single-user notebook servers in ~/assignments,
# with ~/assignments/Welcome.ipynb as the default landing page
# this config could also be put in
# /etc/ipython/ipython_notebook_config.py
# c.Spawner.notebook_dir = '~/assignments'
# c.Spawner.args = ['--NotebookApp.default_url=/notebooks/Welcome.ipynb']

c.Spawner.container_ip = '192.168.23.2'
c.Spawner.hub_ip_connect = pubip
c.Spawner.container_prefix = "jupyter" 
c.Spawner.read_only_volumes = {'/mnt/data/volumes/yt_data': '/mnt/yt'}
c.Spawner.remove_containers = True
