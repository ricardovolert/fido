#!/bin/bash

apt-get -y install python-software-properties
apt-get -y update
DEBIAN_FRONTEND=noninteractive apt-get -y -o Dpkg::Options::="--force-confdef" -o Dpkg::Options::="--force-confold" upgrade

cat >/etc/apt/preferences <<EOM
Package: *
Pin: release a=precise-backports
Pin-Priority: 500
EOM

cat >/etc/apt/sources.list.d/pgdg.list <<EOM
deb http://apt.postgresql.org/pub/repos/apt/ precise-pgdg main
EOM

apt-get install -y wget sudo
wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | sudo apt-key add -

add-apt-repository -y ppa:git-core/ppa
add-apt-repository -y ppa:chris-lea/redis-server
add-apt-repository -y ppa:chris-lea/node.js
add-apt-repository -y ppa:nginx/development

apt-get update
apt-get -y install xvfb 

apt-get -y install vim git postgresql redis-server nginx nodejs python-setuptools python-dev \
   libevent-dev
easy_install pip

CGDEB=Cg-3.1_April2012_x86_64.deb
wget --directory=/tmp http://developer.download.nvidia.com/cg/Cg_3.1/$CGDEB
dpkg -i /tmp/$CGDEB
rm /tmp/$CGDEB

IR_BUILD="InstantReality-Ubuntu-12.04-x64-2.3.0.25550.deb"
wget --directory=/tmp http://x3dom.org/temp/IR/$IR_BUILD
dpkg -i /tmp/$IR_BUILD

# get missing dependencies from dpkg
apt-get -y -f install 
apt-get install xdg-utils libqt4-sql-sqlite
dpkg -i /tmp/$IR_BUILD
rm /tmp/$IR_BUILD

# meshlab
apt-get -y install subversion qt4-dev-tools qtcreator
mkdir -p /opt/build
svn co -r 6131 https://svn.code.sf.net/p/meshlab/code/trunk/meshlab/ /opt/build/meshlab
svn co -r 4880 https://svn.code.sf.net/p/vcg/code/trunk/vcglib/ /opt/build/vcglib

cd /opt/build/meshlab/src/external/structuresynth/ssynth
svn co https://svn.code.sf.net/p/structuresynth/code/trunk/StructureSynth
svn co https://svn.code.sf.net/p/structuresynth/code/trunk/SyntopiaCore
svn co https://svn.code.sf.net/p/structuresynth/code/trunk/ThirdPartyCode

cd /opt/build/meshlab/src/external
qmake -recursive external.pro 
make -j9

cd /opt/build/meshlab/src/external/jhead-2.95
make -f Makefile

cd /opt/build/meshlab/src
qmake -recursive meshlabserver_vmust.pro
make -j9

wget --directory=/tmp http://vcg.isti.cnr.it/nexus/download/nexus.tgz
cd /opt/build
tar xvfz /tmp/nexus.tgz
ln -f -s nexus2.0 nexus
cd /opt/build/nexus/nxsbuild
qmake nxsbuild.pro
make

pip install -r https://raw.github.com/xarthisius/pipeline/master/requirements.txt

cd /home
git clone https://github.com/xarthisius/pipeline

mkdir /tmp/downloads
mkdir /tmp/uploads

pip install supervisor
