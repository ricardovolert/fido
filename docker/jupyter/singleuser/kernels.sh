#!/bin/sh
KERNDIR=/usr/local/share/jupyter/kernels

for pyver in 2 3; do
   for branch in dev stable; do
       sudo -H -u jovyan bash -c "/opt/conda/bin/conda env create -n py${pyver}-${branch} python=${pyver} -f /tmp/yt${branch}.yaml"
       cp -r ${KERNDIR}/python2 $KERNDIR/py${pyver}-${branch}
       sed -i ${KERNDIR}/py${pyver}-${branch}/kernel.json \
          -e "/display_name/ s/Python 2/yt (${branch}) - py${pyver}/" \
          -e "/conda/ s/python2/py${pyver}-${branch}/"
    done
done

rm -rf ${KERNDIR}/python2
