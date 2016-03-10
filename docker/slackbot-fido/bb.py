import os
import re
import urllib2
import json
import requests
import logging
import hglib
import tempfile
import tinydb
from hgbb import get_pr_info, _bb_apicall

outputs = []
DB = tinydb.TinyDB("/mnt/db/slack.json")
JENKINS_TOKEN = os.environ.get("JENKINS_TOKEN")
JENKINS_URL = os.environ.get("JENKINS_URL")
SAGE_START_URL = os.environ.get("SAGE_START_URL")
SAGE_CLIENT_URL = os.environ.get("SAGE_CLIENT_URL", "http://somewhere.org")
SAGE_DISPLAY_URL = SAGE_CLIENT_URL + "/display.html?clientID=0"
REPOS_DIR = "/tmp/bb_repos"


def _get_local_repo(path):
    repo_path = os.path.join(REPOS_DIR, path)
    if not os.path.isdir(repo_path):
        os.makedirs(repo_path)
        repo = hglib.clone("https://bitbucket.org/%s" % path, repo_path)
    repo = hglib.open(repo_path)
    repo.pull()
    repo.update(rev="yt", clean=True)
    repo.close()
    temp_repo = tempfile.mkdtemp()
    hglib.clone(repo_path, temp_repo)
    return temp_repo, hglib.open(temp_repo)


def _build_job(data, prno, docs=False):
    try:
        pr = get_pr_info(None, "yt_analysis/yt", prno)
    except urllib2.HTTPError:
        outputs.append([data['channel'],
                        "Something went wrong. Pester xarthisius"])
        return
    author = pr['author']['display_name']
    if docs:
        msg = "will build docs for PR %i" % prno
        urls = ["%s/job/%s/build?token=%s" % (JENKINS_URL, "yt_docs",
                                              JENKINS_TOKEN)]
    else:
        msg = "will test PR %i by %s" % (prno, author)
        urls = ["%s/job/%s/build?token=%s" % (JENKINS_URL, "yt_testsuite",
                                              JENKINS_TOKEN)]
    params = [
        {'name': 'IRKMSG', 'value': msg},
        {'name': 'YT_REPO', 'value': pr['source']['repository']['full_name']},
        {'name': 'YT_REV', 'value': pr['source']['commit']['hash']},
        {'name': 'YT_DEST', 'value': pr['destination']['commit']['hash']}
    ]
    payload = {
        'json': json.dumps({'parameter': params}),
        'Submit': 'Build'
    }
    for url in urls:
        requests.post(url, data=payload)
    outputs.append([data['channel'], "job submitted"])


class FidoCommand:
    regex = None
    help_msg = None

    def __call__(self, data):
        s = self.regex(data["text"])
        if s is not None:
            if len(s.groups()) > 0:
                self.run(s.groups(), data)

    def run(self, match, data):
        pass


class FidoBuildDocs(FidoCommand):
    regex = re.compile(r'build docs for PR\s?(\d+)', re.IGNORECASE).search

    def run(self, match, data):
        _build_job(data, int(match[0]), docs=True)


class FidoTestPR(FidoCommand):
    regex = re.compile(r'test PR\s?(\d+)', re.IGNORECASE).search

    def run(self, match, data):
        _build_job(data, int(match[0]), docs=False)


class FidoGetPRInfo(FidoCommand):
    regex = re.compile(r'PR\s?(\d+)', re.IGNORECASE).search

    def run(self, match, data):
        try:
            pr = get_pr_info(None, "yt_analysis/yt", int(match[0]))
            outputs.append([data['channel'],
                            pr['links']['html']['href']])
        except urllib2.HTTPError:
            pass


class FidoGetIssueInfo(FidoCommand):
    regex = re.compile(r'#(\d+)').search

    def run(self, match, data):
        try:
            retval = _bb_apicall(None,
                                 'repositories/yt_analysis/yt/issues/%s'
                                 % match[0], None, False, api=1)
            json.loads(retval)
            outputs.append([data['channel'],
                            "https://bitbucket.org/yt_analysis/yt/issue/%s/"
                            % match[0]])
        except IOError:
            pass


class FidoStartSage(FidoCommand):
    regex = re.compile(r'(start sage)', re.IGNORECASE).search

    def run(self, match, data):
        r = requests.get(SAGE_START_URL)
        if r.status_code != requests.codes.ok:
            outputs.append(
                [data['channel'], "Something went wrong :( Poke admin"])
            return

        value = json.loads(r.data)
        sage_url = value['url']
        sage_hash = sage_url.split("/")[-2]
        msg = "Interact: %s\nDisplay: %s\n" % (
            SAGE_CLIENT_URL % sage_hash,
            SAGE_DISPLAY_URL % sage_hash)
        outputs.append([data['channel'], msg])


class FidoUserRepoQuery(FidoCommand):
    regex = re.compile(r'^What is (my repo).*$', re.IGNORECASE).match

    def run(self, match, data):
        dbquery = tinydb.Query()
        repo = DB.search(dbquery.user == data["user"])
        if repo:
            outputs.append([data['channel'], repo[0]["repo"]])
        else:
            outputs.append([data['channel'], "I have no clue"])


class FidoUserRepoKeep(FidoCommand):
    regex = re.compile(r'^(.*/.*) is my repo$').match

    def run(self, match, data):
        dbquery = tinydb.Query()
        if not DB.update({'repo': match[0]},
                         cond=dbquery.user == data["user"]):
            DB.insert({'user': data["user"], 'repo': match[0]})
        outputs.append([data['channel'], "Got it!"])


class FidoUserRepoForget(FidoCommand):
    regex = re.compile(r'^(forget) my repo$').match

    def run(self, match, data):
        dbquery = tinydb.Query()
        if DB.remove(dbquery.user == data["user"]):
            outputs.append([data['channel'], "Roger!"])


class FidoHelpMe(FidoCommand):
    regex = re.compile(r'^.*(fido:? help).*$', re.IGNORECASE).match

    def run(self, match, data):
        msg = ""
        for command in FIDO_COMMANDS:
            msg += "`{}`".format(command.regex.__self__.pattern)
            if command.help_msg is not None:
                msg += " " + command.help_msg
            msg += "\n"
        outputs.append([data['channel'], msg])


FIDO_COMMANDS = [
    FidoGetPRInfo(), FidoGetIssueInfo(), FidoStartSage(), FidoTestPR(),
    FidoBuildDocs(), FidoUserRepoQuery(), FidoUserRepoKeep(),
    FidoUserRepoForget(), FidoHelpMe() 
]


def process_message(data):
    # if data['channel'].startswith("D") and 'text' in data:
    if "text" not in data:
        return

    if "username" in data:
        username = data['username']
        if username == 'yt-fido' or username.startswith("RatThing"):
            logging.info("Won't talk to myself")
            return

    for command in FIDO_COMMANDS:
        command(data)
