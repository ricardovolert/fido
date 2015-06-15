import re
import urllib2
import json
import requests
from hgbb import get_pr_info, _bb_apicall


crontable = []
outputs = []

regprno = re.compile(r'PR\s?(\d+)', re.IGNORECASE)
regissno = re.compile(r'#(\d+)')
builddocs = re.compile(r'build docs for PR\s?(\d+)', re.IGNORECASE)
testpr = re.compile(r'test PR\s?(\d+)', re.IGNORECASE)

TOKEN = "215d73b57c5149a88e23814501690540"
JENKINS_URL = 'http://hub.yt:8080/'
JENKINS = "%s/job/yt_docs/build?token=%s" % (JENKINS_URL, TOKEN)


def build_job(data, prno, docs=False):
    try:
        pr = get_pr_info(None, "yt_analysis/yt", prno)
    except urllib2.HTTPError:
        outputs.append([data['channel'],
                       "Something went wrong. Pester xarthisius"])
        return
    author = pr['author']['display_name']
    if docs:
        msg = "will build docs for PR %i" % prno
        urls = ["%s/job/%s/build?token=%s" % (JENKINS_URL, "yt_docs", TOKEN)]
    else:
        msg = "will test PR %i by %s" % (prno, author)
        urls = ["%s/job/%s/build?token=%s" % (JENKINS_URL, "yt_testsuite_dev", TOKEN),
                "%s/job/%s/build?token=%s" % (JENKINS_URL, "yt_testsuite_py34", TOKEN)]
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
        r = requests.post(url, data=payload)
    outputs.append([data['channel'], "job submitted"])


def process_message(data):
    # if data['channel'].startswith("D") and 'text' in data:
    if 'text' in data:
        s = builddocs.search(data['text'])
        if s is not None:
            match = s.groups()
            if len(match) > 0:
                build_job(data, int(match[0]), docs=True)
            return
        s = testpr.search(data['text'])
        if s is not None:
            match = s.groups()
            if len(match) > 0:
                build_job(data, int(match[0]), docs=False)
            return

        s = regprno.search(data['text'])
        if s is not None:
            match = s.groups()
            if len(match) > 0:
                try:
                    pr = get_pr_info(None, "yt_analysis/yt", int(match[0]))
                    outputs.append([data['channel'],
                                    pr['links']['html']['href']])
                except urllib2.HTTPError:
                    pass
        s = regissno.search(data['text'])
        if s is not None:
            match = s.groups()
            if len(match) > 0:
                try:
                    retval = _bb_apicall(None, 'repositories/yt_analysis/yt/issues/%s'
                                         % match[0], None, False, api=1)
                    issue = json.loads(retval)
                    outputs.append([data['channel'],
                                    "https://bitbucket.org/yt_analysis/yt/issue/%s/"
                                    % match[0]])
                except IOError:
                    pass