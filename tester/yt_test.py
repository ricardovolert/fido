import os
import docker
import tarfile
from cStringIO import StringIO

BASE_URL = os.environ.get('BASE_URL', "tcp://141.142.234.27:2375")
# BASE_URL = 'unix://var/run/docker.sock'

IMAGE_NAME = os.environ.get('IMAGE_NAME', "ytanalysis/yt")
IMAGE_TAG = os.environ.get('IMAGE_TAG', "latest")
IMAGE_REPO = os.environ.get('IMAGE_REPO', "hub.yt")

DEFAULT_IMAGE = "%s/%s:%s" % (IMAGE_REPO, IMAGE_NAME, IMAGE_TAG)
DEFAULT_COMMAND = "nosetests -v units/tests"
DEFAULT_OUTPUT = "unittests.xml"


def run_test(image=DEFAULT_IMAGE,
             command="nosetests -v units/tests",
             output="unittests.xml",
             build_docs=False):
    print("Using image: %s" % image)
    workdir = "/tmp/yt"
    if build_docs:
        workdir = os.path.join(workdir, "doc")
    dcli = docker.Client(base_url=BASE_URL, timeout=360)
    contid = dcli.create_container(
        image=image,
        command=command,
        volumes=["/mnt/yt"],
        working_dir=workdir,
    )
    dcli.start(contid,
               binds={"/mnt/data/volumes/yt_data/": {"bind": "/mnt/yt/"}})

    for line in  dcli.logs(contid, stdout=True, stderr=True,
                           stream=True, timestamps=False):
        print line
    retcode = dcli.wait(contid)

    try:
        fo = StringIO(dcli.copy(contid, "/tmp/yt/nosetests.xml").read())
        tar = tarfile.open(mode="r", fileobj=fo)
        with open(output, 'w') as fh:
            fh.write(tar.extractfile('nosetests.xml').read())
    except docker.errors.APIError as e:
        print("nosetests.xml not found :(")

    if build_docs:
        try:
            with open("docs.tar", "w") as fh:
                fh.write(dcli.copy(contid, "/tmp/yt/doc/build/html/").read())
        except docker.errors.APIError as e:
            print("extracting docs failed :(")

    dcli.remove_container(contid, force=True)
    os._exit(retcode)
