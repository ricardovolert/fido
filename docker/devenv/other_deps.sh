#/bin/bash

# rockstar
mkdir -p /usr/local/src
cd /usr/local/src
hg clone https://bitbucket.org/MatthewTurk/rockstar
cd rockstar
hg update -C tip
rm -rf .hg
make lib RNG_FLAGS="-DRESET_RNG_STREAM"
cp librockstar.so /usr/lib64

# SZpack
cd /tmp/SZpack.v1.1.1/
make
cd python
python2 setup.py install && cp SZpack.py /usr/lib64/python2.7/site-packages/
python3 setup.py install && cp SZpack.py /usr/lib64/python3.4/site-packages/
cd /tmp
rm -rf /tmp/SZ*

# runipy
cd /tmp
git clone https://github.com/paulgb/runipy.git
cd runipy
python2 setup.py install
#python3 setup.py install
cd /tmp
rm -rf runipy

#### pyne
# Instal MOAB
mkdir /tmp/moab
cd /tmp/moab
wget http://ftp.mcs.anl.gov/pub/fathom/moab-4.6.2.tar.gz
tar zxvf moab-4.6.2.tar.gz
rm moab-4.6.2.tar.gz
mkdir build
cd build
../moab-4.6.2/configure --enable-shared && make && make install
cd /tmp && rm -rf /tmp/moab

# Install PyTAPS
cd /tmp
wget https://pypi.python.org/packages/source/P/PyTAPS/PyTAPS-1.4.tar.gz
tar zxvf PyTAPS-1.4.tar.gz
cd PyTAPS-1.4/
python2 setup.py install
#python3 setup.py install
cd /tmp && rm -rf PyTAPS*

# Install PyNE
cd /tmp
git clone https://github.com/pyne/pyne.git
cd pyne && python setup.py install --hdf5=/usr
cd scripts && ./nuc_data_make
cd /tmp && rm -rf /tmp/pyne

# JSAnimation
cd /tmp 
git clone https://github.com/jakevdp/JSAnimation.git
cd JSAnimation 
python2 setup.py install
#python3 setup.py install
cd /tmp && rm -rf JSAnimation

# Sphinx
cd /tmp
hg clone https://bitbucket.org/xarthisius/sphinx
cd sphinx
python2 setup.py install
#python3 setup.py install
cd /tmp && rm -rf sphinx

# thingking
cd /tmp
wget https://pypi.python.org/packages/source/t/thingking/thingking-1.0.2.tar.gz
tar xvf thingking-1.0.2.tar.gz
cd thingking-1.0.2
python2 setup.py install
cd /tmp && rm -rf thingking*
