#!/bin/sh
KERNDIR=/opt/conda/share/jupyter/kernels/python3
UKERNDIR=$HOME/.local/share/jupyter/kernels/

mkdir -p $UKERNDIR

for pyver in 2 3; do
   for branch in dev stable; do
       sed -e "/dependencies/ a- python=${pyver}" /tmp/yt${branch}.yaml > /tmp/${pyver}yt${branch}.yaml
       /opt/conda/bin/conda env create -q -n py${pyver}-${branch} -f /tmp/${pyver}yt${branch}.yaml
       cp -r ${KERNDIR} $UKERNDIR/py${pyver}-${branch}
       sed -i ${UKERNDIR}/py${pyver}-${branch}/kernel.json \
          -e "/display_name/ s/Python 3/yt (${branch}) - py${pyver}/" \
          -e "/conda/ s:/opt/conda:&/envs/py${pyver}-${branch}:"
    done
done

sed -e "\$ac.KernelSpecManager.whitelist = {'py2-dev', 'py2-stable', 'py3-dev', 'py3-stable'}" \
    -e "\$ac.MappingKernelManager.default_kernel_name = 'py2-dev'" \
    -i $HOME/.jupyter/jupyter_notebook_config.py
