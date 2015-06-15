#!/usr/bin/env python2
from __future__ import print_function

import os
import glob
import sys
import etcd
import json
import time
import urllib3.exceptions
import signal
import subprocess
from string import Template


PREFIX = os.environ.get("PROXY_PREFIX", "/sage")
HOSTNAME = os.environ.get("HOSTNAME")

RPROXY = Template('''
	location /sage/$prefix {
		proxy_set_header X-Real-IP $$remote_addr;
		proxy_set_header X-Forwarded-For $$proxy_add_x_forwarded_for;
		proxy_set_header Host $$http_host;
		proxy_set_header X-NginX-Proxy true;
		proxy_set_header X-Forwarded-Proto $$scheme;

		# WebSocket support
		proxy_http_version 1.1;
		proxy_set_header Upgrade $$http_upgrade;
		proxy_set_header Connection "upgrade";
		proxy_read_timeout 86400;
		rewrite  /sage/$prefix(/.*)$$ $$1 break;
		proxy_pass https://192.168.23.2:$port/;
	}

''')


def filter_prefix(d, pref):
    return [k for k in d.keys() if k.startswith("%s/%s/" % (PREFIX, pref))]


class log:

    @staticmethod
    def info(msg):
        sys.stderr.write("=> " + msg + "\n")

    @staticmethod
    def error(msg, e=None):
        sys.stderr.write("=! %s : %s\n" % (msg, str(e)))


class State:

    def __init__(self):
        self.proxies = set()


class Config:

    def __init__(self, host_ip):
        self.state = State()
        self.client = etcd.Client(host=host_ip, port=4001)

    def sync(self, children):
        etc = dict((child.key, child.value) for child in children)

        proxies = set(os.path.relpath(k, "%s/proxies" % PREFIX)
                      for k in filter_prefix(etc, 'proxies'))
        self.sync_proxies(proxies)

    def create_proxy(self, proxy):
        path = os.path.join(PREFIX, 'proxies', proxy)
        target = self.client.read(path)
        fname = "/etc/nginx/rproxy/%s.conf" % proxy
        port = target.value.rsplit(':')[-1].strip('/')
        with open(fname, "w") as fh:
            fh.write(RPROXY.substitute(prefix=proxy, port=port))
        log.info("I added proxy /%s for %s" % (proxy, target.value))

    def delete_proxy(self, proxy):
        # path = os.path.join(PREFIX, 'proxies', proxy)
        fname = "/etc/nginx/rproxy/%s.conf" % proxy
        if os.path.isfile(fname):
            os.remove(fname)
            log.info("I deleted proxy /%s" % proxy)

    def sync_proxies(self, proxies):
        proxies_to_add = proxies - self.state.proxies
        for proxy in proxies_to_add:
            log.info("Creating proxy %s" % proxy)
            try:
                self.create_proxy(proxy)
                self.state.proxies.add(proxy)
            except Exception as e:
                log.error("Failed to create proxy %s" % proxy, e)
        proxies_to_rm = self.state.proxies - proxies - {'/'}
        for proxy in proxies_to_rm:
            log.info("Removing proxy %s" % proxy)
            try:
                self.delete_proxy(proxy)
                self.state.proxies.remove(proxy)
            except Exception as e:
                log.error("Failed to remove proxy %s" % proxy, e)
        for oldproxy in glob.glob("/etc/nginx/rproxy/*.conf"):
            proxy = os.path.splitext(os.path.basename(oldproxy))[0]
            if proxy not in self.state.proxies:
                self.delete_proxy(proxy)
        log.info("Reloading nginx")
        nginx_pid = int(
            subprocess.check_output(["pgrep", "-u", "root", "nginx"]).strip()
        )
        os.kill(nginx_pid, signal.SIGHUP)


if __name__ == '__main__':
    host_ip = os.environ.get('COREOS_PRIVATE_IPV4', "192.168.23.2")
    log.info("Connecting to etcd at %s" % host_ip)

    init = False
    config = Config(host_ip)
    config.client.set(PREFIX + '/service',
                      json.dumps({'host': host_ip, 'port': 8000}))

    while True:
        try:
            if not init:
                r = config.client.read(PREFIX, recursive=True)
                init = True
            else:
                config.client.read(PREFIX, recursive=True, wait=True)
                r = config.client.read(PREFIX, recursive=True)
            config.sync(r.children)
        except urllib3.exceptions.ReadTimeoutError as e:
            time.sleep(1)
        except KeyError as e:
            time.sleep(1)
        except etcd.EtcdException as e:
            time.sleep(1)
