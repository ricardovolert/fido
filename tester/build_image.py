#!/usr/bin/python
from string import Template
import tempfile
import json
import os
import sys
import shutil
import docker


BASE_URL = os.environ.get('BASE_URL', "tcp://141.142.234.27:2375")
dockerfile_temp = Template('''FROM hub.yt/yt_analysis/devenv
ENV PYTHONPATH="/tmp/yt"
ADD ./$script /tmp/yt/run.sh
WORKDIR /tmp/yt
RUN bash /tmp/yt/run.sh
CMD ["sleep", "7200"]''')

runner_temp = Template('''#!/bin/bash
if [[ $yt_repo == yt_analysis/yt ]] ; then
   hg update -r $yt_rev
else
   hg update -C $yt_dest
   hg pull -u https://bitbucket.org/$yt_repo -r $yt_rev
   HEADS=`hg heads yt --template "{rev}\\n" | wc -l`
   if [ $$HEADS -gt 1 ] ; then
      if (hg merge -r $yt_dest 2>&1) ; then
          echo "auto merge"
      else
          echo "merge failed (please resolve manually)"
      fi
   fi
fi

hg id
export PYTHONPATH=$$PWD
export YT_BUILD=$$PWD

sed -i -e 's:/does/not/exist:/mnt/yt:g' \
    -e '/suppressstreamlogging/ s/False/True/g' yt/config.py
sed -i -e '/^where=/d' *.cfg
sed -e '/#html_last_updated_fmt/ s/#//' -i doc/source/conf.py
sed -i -e '/^SPHINXBUILD/ s/sphinx-build/& -j 8/g' doc/Makefile
sed -e '/download_datasets =/ s/True/False/' \
    -i doc/source/quickstart/1\)_Introduction.ipynb

echo "/usr/local/src/rockstar" > rockstar.cfg
CFLAGS="-Wno-cpp -fno-strict-aliasing -O3 -march=native -pipe" \
    python setup.py egg_info build_ext -i
python setup.py sdist''')

runner = runner_temp.substitute(
    yt_rev=os.environ.get("YT_REV", "yt"),
    yt_dest=os.environ.get("YT_DEST", "yt"),
    yt_repo=os.environ.get("YT_REPO", "yt_analysis/yt")
)

build_dir = tempfile.mkdtemp()
with open(os.path.join(build_dir, "run.sh"), 'w') as fh:
    fh.write(runner)
with open(os.path.join(build_dir, "Dockerfile"), 'w') as fh:
    fh.write(dockerfile_temp.substitute(script="run.sh"))

tag = os.environ.get("IMAGE_REPO", "hub.yt") + "/"
tag += os.environ.get("IMAGE_NAME", "ytanalysis/yt") + ":"
tag += os.environ.get("IMAGE_TAG", "latest-py2.7")

cli = docker.Client(base_url=BASE_URL, timeout=360)
for line in cli.build(path=build_dir, rm=True, tag=tag, nocache=True,
                      pull=True, forcerm=True, timeout=60):
    sys.stdout.write(json.loads(line)["stream"])
shutil.rmtree(build_dir)
