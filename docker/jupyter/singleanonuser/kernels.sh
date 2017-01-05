#!/bin/bash
export PATH=/opt/conda/bin:$PATH
export CONDA_ENVS=/opt/conda/envs

for pyver in 2 3; do
   for branch in dev stable; do
       sed -e "/dependencies/ a- python=${pyver}" /tmp/yt${branch}.yaml > /tmp/${pyver}yt${branch}.yaml
       conda env create -q -p $CONDA_ENVS/py${pyver}-${branch} -f=/tmp/${pyver}yt${branch}.yaml
       source activate $CONDA_ENVS/py${pyver}-${branch}
       python -m ipykernel install --user --name "py${pyver}-${branch}" --display-name "py${pyver} (${branch})"
       jupyter nbextension enable --py widgetsnbextension --sys-prefix
    done
done

sed -e "\$ac.KernelSpecManager.whitelist = {'py2-dev', 'py2-stable', 'py3-dev', 'py3-stable'}" \
    -e "\$ac.MappingKernelManager.default_kernel_name = 'py2-dev'" \
    -i $HOME/.jupyter/jupyter_notebook_config.py
