import os
import re
import urllib2
import json
import requests
import logging
from hgbb import get_pr_info, _bb_apicall

crontable = []
outputs = []

# regex needs to create group
regprno = re.compile(r'PR\s?(\d+)', re.IGNORECASE)
regissno = re.compile(r'#(\d+)')
builddocs = re.compile(r'build docs for PR\s?(\d+)', re.IGNORECASE)
testpr = re.compile(r'test PR\s?(\d+)', re.IGNORECASE)
startsage = re.compile(r'(start sage)', re.IGNORECASE)

JENKINS_TOKEN = os.environ.get("JENKINS_TOKEN")
JENKINS_URL = os.environ.get("JENKINS_URL")
SAGE_START_URL = os.environ.get("SAGE_START_URL")
SAGE_CLIENT_URL = os.environ.get("SAGE_CLIENT_URL", "http://somewhere.org")
SAGE_DISPLAY_URL = SAGE_CLIENT_URL + "/display.html?clientID=0"


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
        urls = ["%s/job/%s/build?token=%s" % (JENKINS_URL, "yt_testsuite_dev",
                                              JENKINS_TOKEN),
                "%s/job/%s/build?token=%s" % (JENKINS_URL, "yt_testsuite_py34",
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

    def __call__(self, data):
        s = self.regex(data["text"])
        if s is not None:
            if len(s.groups()) > 0:
                self.run(s.groups(), data)

    def run(self, match, data):
        pass


class FidoBuildDocs(FidoCommand):
    regex = builddocs.search

    def run(self, match, data):
        _build_job(data, int(match[0]), docs=True)


class FidoTestPR(FidoCommand):
    regex = testpr.search

    def run(self, match, data):
        _build_job(data, int(match[0]), docs=False)


class FidoGetPRInfo(FidoCommand):
    regex = regprno.search

    def run(self, match, data):
        try:
            pr = get_pr_info(None, "yt_analysis/yt", int(match[0]))
            outputs.append([data['channel'],
                            pr['links']['html']['href']])
        except urllib2.HTTPError:
            pass


class FidoGetIssueInfo(FidoCommand):
    regex = regissno.search

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
    regex = startsage.search

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

FIDO_COMMANDS = [
    FidoGetPRInfo(), FidoGetIssueInfo(), FidoStartSage(), FidoTestPR(),
    FidoBuildDocs()
]


def process_message(data):
    # if data['channel'].startswith("D") and 'text' in data:
    if "text" not in data or "username" not in data:
        return
    username = data['username']
    if username == 'yt-fido' or username.startswith("RatThing"):
        logging.info("Won't talk to myself")
        return

    for command in FIDO_COMMANDS:
        command(data)
