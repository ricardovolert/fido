# -*- coding: utf-8 -*-
#
# bitbucket.org mercurial extension
#
# Copyright (c) 2009, 2010, 2011 by Armin Ronacher, Georg Brandl.
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation; either version 2 of the License, or (at your option) any later
# version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#
"""convenient access to bitbucket.org repositories and features

This extension has two purposes:

- access bitbucket repositories via short URIs like ``bb:[name/]repo``
- conveniently do several bitbucket.org operations on the command line

Configuration::

    [bb]
    username = your bitbucket username
    password = your bitbucket http password (otherwise you'll be asked)
    default_method = the default checkout method to use (ssh or http)
    upstream = the repo to look at for pull requests and the like

There is one additional configuration value that makes sense only in
repository-specific configuration files::

    ignore_forks = comma-separated list of forks you'd like to ignore in
                   bbforks

The forks are given by bitbucket repository names (``username/repo``).

Implemented URL schemas, usable instead of ``https://bitbucket.org/...``:

bb://repo
    clones your own "repo" repository, checkout via default method
bb://username/repo
    clones the "repo" repository by username, checkout via default method
bb+http://repo
    clones your own "repo" repository, checkout via http
bb+http://username/repo
    clones the "repo" repository by username, checkout via http
bb+ssh://repo
    clones your own "repo" repository, checkout via ssh
bb+ssh://username/repo
    clones the "repo" repository by username, checkout via ssh

Note: you can omit the two slashes (e.g. ``bb:user/repo``) when using the
URL on the command line.  It will *not* work when put into the [paths]
entry in hgrc.
"""

try:
    from mercurial.httprepo import instance as httprepo_instance
    from mercurial.sshrepo import sshrepository as sshrepo_instance
except ImportError:  # for 2.3
    from mercurial.httppeer import instance as httprepo_instance
    from mercurial.sshpeer import instance as sshrepo_instance

from mercurial import hg, url, commands, util, \
    error, extensions, revset

import os
import base64
import urllib
import urllib2
import urlparse
import json
import re

# utility functions


def get_username(ui):
    """Return the bitbucket username or guess from the login name."""
    username = ui.config('bb', 'username', None)
    if username:
        return username
    import getpass
    username = getpass.getuser()
    ui.status('using system user %r as username' % username)
    return username


def parse_repopath(path):
    if '://' in path:
        parts = urlparse.urlsplit(path)
        # http or ssh full path
        if parts[1].endswith('bitbucket.org'):
            return parts[2].strip('/')
        # bitbucket path in schemes style (bb://name/repo)
        elif parts[0].startswith('bb'):
            # parts[2] already starts with /
            return ''.join(parts[1:3]).strip('/')
    # bitbucket path in hgbb style (bb:name/repo)
    elif path.startswith('bb:'):
        return path[3:]
    elif path.startswith('bb+') and ':' in path:
        return path.split(':')[1]


def get_bbreponame(ui, repo, opts, upstream = False):
    reponame = opts.get('reponame', None)
    constructed = False
    if not reponame and upstream:
        reponame = ui.config('bb', 'upstream', None)
    if not reponame:
        # try to guess from the "default" or "default-push" repository
        paths = ui.configitems('paths')
        for name, path in paths:
            if name == 'default' or name == 'default-push':
                reponame = parse_repopath(path)
                if reponame:
                    break
        else:
            # guess from repository pathname
            reponame = os.path.split(repo.root)[1]
        constructed = True
    if '/' not in reponame:
        reponame = '%s/%s' % (get_username(ui), reponame)
        constructed = True
    # if we guessed or constructed the name, print it out for the user to avoid
    # unwanted surprises
    if constructed:
        ui.status('using %r as repo name\n' % reponame)
    return reponame


# bb: schemes repository classes

class bbrepo(object):

    """Short URL to clone from or push to bitbucket."""

    def __init__(self, factory, url):
        self.factory = factory
        self.url = url

    def instance(self, ui, url, create):
        scheme, path = url.split(':', 1)
        # strip the occasional leading // and
        # the tailing / of the new normalization
        path = path.strip('/')
        username = get_username(ui)
        if '/' not in path:
            path = username + '/' + path
        password = ui.config('bb', 'password', None)
        if password is not None:
            auth = '%s:%s@' % (username, password)
        else:
            auth = username + '@'
        formats = dict(
            path=path.rstrip('/') + '/',
            auth=auth
        )
        return self.factory(ui, self.url % formats, create)


class auto_bbrepo(object):

    def instance(self, ui, url, create):
        method = ui.config('bb', 'default_method', 'https')
        if method not in ('ssh', 'http', 'https'):
            raise util.Abort('Invalid config value for bb.default_method: %s'
                             % method)
        if method == 'http':
            method = 'https'
        return hg.schemes['bb+' + method].instance(ui, url, create)


def list_forks(ui, reponame):
    retval = _bb_apicall(ui, 'repositories/%s/forks' % (reponame),
                         None, False, api=2)
    data = json.loads(retval)
    if 'size' not in data:
        return None
    if data['pagelen'] > 1:
        ui.status("There are %i forks. I will show only %i of them\n" %
                  (data['size'], len(data['values'])))
    return [fork['full_name'] for fork in data['values']]


def list_prs(ui, reponame):
    print ui, reponame
    prs = []
    page_id = 1
    while 1:
        data = json.loads(_bb_apicall(ui,
                             'repositories/%s/pullrequests?length=100&page=%s'
                             % (reponame, page_id),
                             None, False, api=2, strip_slash = True))
        if 'size' not in data:
            return None
        prs += [(pr['id'], pr['author']['display_name'], pr['title'])
                for pr in data['values']]
        if not data.get('next', None): break
        page_id += 1
    return prs


def get_pr(ui, reponame, repo, prn):
    retval = _bb_apicall(ui, 'repositories/%s/pullrequests/%s'
                         % (reponame, prn), None, False, api=2)
    data = json.loads(retval)
    commit_hash = data['source']['commit']['hash']
    source_repo = data['source']['repository']["full_name"]
    incoming_repo = 'bb://%s' % (source_repo)
    ui.status('Pulling %s from %s\n' % (commit_hash, incoming_repo))
    ret = commands.pull(ui, repo, source = incoming_repo,
                        rev = [commit_hash],
                        update = False)
    ui.status('Update to %s to test PR %s\n' % (commit_hash, prn))

def get_pr_info(ui, reponame, prn):
    retval = _bb_apicall(ui, 'repositories/%s/pullrequests/%s'
                         % (reponame, prn), None, False, api=2)
    data = json.loads(retval)
    return data

def display_pr_info(ui, data):
    ui.status('\n')
    ui.status('TITLE:      %s\n' % data['title'])
    ui.status('URL:        %s\n' % data['links']['html']['href'])
    ui.status('AUTHOR:     %s (%s)\n' % (data['author']['display_name'],
                                   data['author']['username']))
    ui.status('STATUS:     %s\n' % data['state'])
    if data['state'] != 'OPEN':
        ui.status('CLOSED BY:  %s (%s)\n' % (data['closed_by']['display_name'],
                                             data['closed_by']['username']))
    ui.status('SOURCE:     %s\n' % data['source']['repository']["full_name"])
    ui.status('COMMIT:     %s\n' % (data['source']['commit']['hash']))
    ui.status('\nDESCRIPTION:\n\n%s\n' % data['description'])

def issue_pr(ui, title, desc, downstream, source_branch, source_rev,
             upstream, dest_branch):
    data = {
            'title': title,
            'description': desc,
            'source': {
                "branch": {"name": source_branch},
                "repository": {"full_name": downstream},
                "commit": {"hash": source_rev},
            },
            'destination': {
                "branch": {"name": dest_branch},
            },
            # for later:
            #"reviewers": [
            #    {"username": reviewer1},
            #    {"username": reviewer2},
            #],
            "close_source_branch": False,
    }
    retval = _bb_apicall(ui, 'repositories/%s/pullrequests'
                         % (upstream), data, True, api=2)
    retval = json.loads(retval)
    return retval

# revsets

def prhead(repo, subset, x):
    """``prhead(prnumber, [reponame])``
    The head changeset of a given pull request.
    """
    args = revset.getargs(x, 1, 2,
            "arguments must include PR number and optional repo name")
    if not args[0][0] == 'symbol':
        raise util.Abort('PR must be a number')
    prn = args[0][1]
    if len(args) == 1:
        reponame = get_bbreponame(repo.ui, repo, {}, True)
    else:
        reponame = args[1]
    pr_info = get_pr_info(repo.ui, reponame, prn)
    commit = pr_info['source']['commit']['hash']
    return revset.baseset([repo[commit].rev()])

def pr_contents(repo, subset, x):
    """``pr(prnumber, [reponame])``
    The changesets included in a given pull request.
    """
    args = revset.getargs(x, 1, 2,
            "arguments must include PR number and optional repo name")
    if not args[0][0] == 'symbol':
        raise util.Abort('PR must be a number')
    prn = args[0][1]
    if len(args) == 1:
        reponame = get_bbreponame(repo.ui, repo, {}, True)
    else:
        reponame = args[1]
    # Now we have to page through our results.
    commits = []
    page_id = 1
    while 1:
        commit_list = json.loads(_bb_apicall(repo.ui,
            'repositories/%s/pullrequests/%s/commits?length=100&page=%s'
            % (reponame, prn, page_id), None, False, 2, True))
        commits += [c['hash'] for c in commit_list['values']]
        if not commit_list.get('next', None): break
        page_id += 1
    return revset.baseset([repo[commit].rev() for commit in commits]) & subset

# new commands

FULL_TMPL = '''\xff{rev}:{node|short} {date|shortdate} {author|user}: \
{desc|firstline|strip}\n'''


def bb_prs(ui, repo, **opts):
    '''list all pull requests of a current bitbucket repo

    An explicit bitbucket reponame (``username/repo``) can be given with the
    ``-n`` option.
    '''

    reponame = get_bbreponame(ui, repo, opts, True)
    if (opts.get('pullrequest')):
        get_pr(ui, reponame, repo, opts.get('pullrequest'))
    elif (opts.get('pullrequestinfo')):
        data = get_pr_info(ui, reponame, opts.get('pullrequestinfo'))
        display_pr_info(ui, data)
    else:
        prs = list_prs(ui, reponame)
        if not prs:
            ui.status('%s has no pull requests\n' % reponame)
            return
        for pid, author, title in prs:
            ui.status("PR%i by %s: %s\n" % (pid, author, title))

_desc = """


HG: Enter pull request description.
HG: Lines beginning with 'HG:' are removed.
HG: Leave description empty to abort commit.
"""

def bb_newpr(ui, repo, **opts):
    '''issue a new pull request to a bitbucket repo

    An explicit upstream bitbucket reponame (``username/repo``) can be given
    with the ``-n`` option, but otherwise the configured upstream destination
    will be used.

    The revision to be used as the head in the pull request can be specified,
    as well as a title and description.  If either the title or description are
    not specified, a prompt will be issued for them.
    '''
    upstream = get_bbreponame(ui, repo, opts, True)
    current = get_bbreponame(ui, repo, {}, False)
    title = opts.get('title')
    if not title:
        title = ui.prompt('Pull request title? ', '')
    if not title:
        raise util.Abort('A title is required.')
    desc = opts.get('desc')
    if not desc:
        desc = ui.edit(_desc, ui.username())
        desc = re.sub("(?m)^HG:.*(\n|$)", "", desc)
    if not desc.strip():
        raise util.Abort('Description empty; aborting.')
    rev = opts.get('rev')
    if not rev: rev = '.'
    ctx = repo[rev]
    rev = str(ctx)
    source_branch = ctx.branch()
    dest_branch = opts.get('branch') or source_branch
    ui.status('Issuing pull request of %s from %s to %s\n'
            % (ctx, current, upstream))
    ret = issue_pr(ui, title, desc,
                   current, source_branch, rev,
                   upstream, dest_branch)
    # ret will either be a dict from the results or None
    if not ret: return -1
    ui.status('Pull request issued:\n    %s\n' % \
            (ret['links']['html']['href']))

def bb_forks(ui, repo, **opts):
    '''list all forks of this repo at bitbucket

    An explicit bitbucket reponame (``username/repo``) can be given with the
    ``-n`` option.

    With the ``-i`` option, check each fork for incoming changesets.  With the
    ``-i -f`` options, also show the individual incoming changesets like
    :hg:`incoming` does.

    If ``-u`` is specified, the forks of the configured ``upstream`` value will
    be listed by default instead.
    '''

    upstream = opts.get('upstream', False)
    reponame = get_bbreponame(ui, repo, opts, upstream)
    ui.status('getting descendants list\n')
    forks = list_forks(ui, reponame)
    if not forks:
        ui.status('this repository has no forks yet\n')
        return
    # filter out ignored forks
    ignore = set(ui.configlist('bb', 'ignore_forks'))
    forks = [name for name in forks if name not in ignore]

    hgcmd = None
    if opts.get('incoming'):
        hgcmd, hgcmdname = commands.incoming, "incoming"
    elif opts.get('outgoing'):
        hgcmd, hgcmdname = commands.outgoing, "outgoing"
    if hgcmd:
        templateopts = {'template': opts.get('full') and FULL_TMPL or '\xff'}
        for name in forks:
            ui.status('looking at %s\n' % name)
            try:
                ui.quiet = True
                ui.pushbuffer()
                try:
                    hgcmd(ui, repo, 'bb://' + name, bundle='',
                          force=False, newest_first=True,
                          **templateopts)
                finally:
                    ui.quiet = False
                    contents = ui.popbuffer(True)
            except (error.RepoError, util.Abort), msg:
                ui.warn('Error: %s\n' % msg)
            else:
                if not contents:
                    continue
                number = contents.count('\xff')
                if number:
                    ui.status('%d %s changeset%s found in bb://%s\n' %
                              (number, hgcmdname, number >
                               1 and 's' or '', name),
                              label='status.modified')
                ui.write(contents.replace('\xff', ''), label='log.changeset')
    else:
        for name in forks:
            ui.status('bb://%s\n' % name)


def _bb_apicall(ui, endpoint, data, use_pass=True, api=1, strip_slash = False):
    uri = 'https://api.bitbucket.org/%i.0/%s/' % (api, endpoint)
    if strip_slash:
        uri = uri[:-1]
    # since bitbucket doesn't return the required WWW-Authenticate header when
    # making a request without Authorization, we cannot use the standard
    # urllib2 auth handlers; we have to add the requisite header from the start
    if data is None:
        headers = {}
    elif api == 1:
        data = urllib.urlencode(data)
        headers = {}
    elif api == 2:
        data = json.dumps(data)
        headers = {'Content-Type': 'application/json'}
    req = urllib2.Request(uri, data, headers)
    #ui.status("Accessing %s" % uri)
    if use_pass:
        # at least re-use Mercurial's password query
        passmgr = url.passwordmgr(ui)
        passmgr.add_password(None, uri, get_username(ui), '')
        upw = '%s:%s' % passmgr.find_user_password(None, uri)
        req.add_header('Authorization', 'Basic %s' %
                       base64.b64encode(upw).strip())
    return urllib2.urlopen(req).read()


def bb_create(ui, reponame, **opts):
    data = {
        'name': reponame,
        'description': opts.get('description'),
        'language': opts.get('language'),
        'website': opts.get('website'),
        'is_private': opts.get('private'),
        'scm': 'hg',
    }
    _bb_apicall(ui, 'repositories', data)
    # if this completes without exception, assume the request was successful,
    # and clone the new repo
    if opts['noclone']:
        ui.write('repository created\n')
    else:
        ui.write('repository created, cloning...\n')
        commands.clone(ui, 'bb://' + reponame)


def bb_followers(ui, repo, **opts):
    '''list all followers of this repo at bitbucket

    An explicit bitbucket reponame (``username/repo``) can be given with the
    ``-n`` option.
    '''
    reponame = get_bbreponame(ui, repo, opts)
    ui.status('getting followers list\n')
    retval = _bb_apicall(ui, 'repositories/%s/followers' % (reponame),
                         None, False)
    followers = json.loads(retval)
    ui.write("List of followers:\n")
    encode = lambda t: t.encode('utf-8') if isinstance(t, unicode) else t
    for follower in sorted(followers.get(u'followers', [])):
        ui.write("    %s (%s %s)\n" % tuple(map(encode, (
            follower['username'],
            follower['first_name'],
            follower['last_name']))))


def bb_link(ui, repo, filename=None, **opts):
    '''Display a bitbucket link to the repository or
       the specific file if given'''
    # XXX: might not work on windows, because it uses \ to separate paths
    lineno = opts.get('lineno')
    reponame = get_bbreponame(ui, repo, opts)
    nodeid = str(repo[None])
    if nodeid.endswith('+'):
        # our wc is dirty, just take the node id and be happy
        nodeid = nodeid[:-1]
    if filename:
        path = os.path.relpath(filename, repo.root)
    else:
        path = ''
    url = 'http://bitbucket.org/%s/src/%s/%s'
    url = url % (reponame, nodeid, path)
    if lineno != -1:
        url += '#cl-' + str(lineno)
    ui.write(url + '\n')


def clone(orig, ui, source, dest=None, **opts):
    if source[:2] == 'bb' and ':' in source:
        protocol, rest = source.split(':', 1)
        if rest[:2] != '//':
            source = '%s://%s' % (protocol, rest)
    return orig(ui, source, dest, **opts)


def uisetup(ui):
    extensions.wrapcommand(commands.table, 'clone', clone)


hg.schemes['bb'] = auto_bbrepo()
hg.schemes['bb+http'] = bbrepo(
    httprepo_instance, 'https://%(auth)sbitbucket.org/%(path)s')
hg.schemes['bb+https'] = bbrepo(
    httprepo_instance, 'http://%(auth)sbitbucket.org/%(path)s')
hg.schemes['bb+ssh'] = bbrepo(
    sshrepo_instance, 'ssh://hg@bitbucket.org/%(path)s')

cmdtable = {
    'bbforks':
    (bb_forks,
     [('n', 'reponame', '',
       'name of the repo at bitbucket (else guessed from repo dir)'),
      ('i', 'incoming', None, 'look for incoming changesets'),
      ('o', 'outgoing', None, 'look for outgoing changesets'),
      ('f', 'full', None, 'show full incoming info'),
      ('u', 'upstream', None, 'look at [bb] upstream forks'),
      ],
     'hg bbforks [-i/-o [-f]] [-n reponame]'),
    'bbprs':
    (bb_prs,
     [('n', 'reponame', '',
       'name of the repo at bitbucket (else guessed from repo dir)'),
      ('p', 'pullrequest', '', 'fetch specific pull request'),
      ('i', 'pullrequestinfo', '', 'display info about pull request')
      ],
     'hg bbprs [-p pullrequest] [-n reponame] [-i pullrequest]'),
    'bbnewpr':
    (bb_newpr,
     [('t', 'title', '', 'title of pull request'),
      ('r', 'rev', '', 'revision to issue as pull request'),
      ('d', 'desc', '', 'description of pull request'),
      ('n', 'reponame', '', 'name of the upstream repo'),
      ('b', 'branch', '', 'destination branch'),
      ],
     'hg newpr [-t title] [-r rev] [-d desc] [-n reponame]'),
    'bbcreate':
    (bb_create,
     [('d', 'description', '', 'description of the new repo'),
      ('l', 'language', '', 'programming language'),
      ('w', 'website', '', 'website of the project'),
      ('p', 'private', None, 'is this repo private?'),
      ('n', 'noclone', None, 'skip cloning?'),
      ],
     'hg bbcreate [-d desc] [-l lang] [-w site] [-p] [-n] reponame'),
    'bbfollowers':
    (bb_followers,
     [('n', 'reponame', '',
       'name of the repo at bitbucket (else guessed from repo dir)'),
      ],
     'hg bbcreate [-d desc] [-l lang] [-w site] reponame'),
    'bblink':
    (bb_link,
     [('l', 'lineno', -1, 'line number')],
     'hg bblink [-l lineno] filename'),
}

#commands.norepo += ' bbcreate'

def extsetup(ui):
    revset.symbols['prhead'] = prhead
    revset.symbols['pr'] = pr_contents
