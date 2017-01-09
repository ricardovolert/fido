FROM jupyter/base-notebook:latest

MAINTAINER Data Exploration Lab <dxl@ncsa.illinois.edu>

USER root
COPY ./envs /tmp/
COPY kernels.sh /tmp/kernels.sh
RUN chmod +x /tmp/kernels.sh


USER jovyan
RUN pip install widgetsnbextension  && \
   jupyter nbextension enable --py --sys-prefix widgetsnbextension
COPY ./yt_config /home/jovyan/.yt/config
RUN /tmp/kernels.sh
COPY ./logo.png /home/jovyan/.jupyter/custom/logo.png
COPY ./custom.css /home/jovyan/.jupyter/custom/custom.css
COPY ./hm2012_hr.h5 /home/jovyan/.trident/hm2012_hr.h5
COPY ./config.tri /home/jovyan/.trident/config.tri

RUN find /opt -name "sdf" -type d -exec sed -i {}/data_structures.py -e 's/float32/float64/' \;

RUN conda install jupyterlab

#RUN wget -q "https://bitbucket.org/yt_analysis/yt/raw/tip/doc/source/quickstart/1)_Introduction.ipynb" && \
#    wget -q "https://bitbucket.org/yt_analysis/yt/raw/tip/doc/source/quickstart/2)_Data_Inspection.ipynb" && \
#    wget -q "https://bitbucket.org/yt_analysis/yt/raw/tip/doc/source/quickstart/3)_Simple_Visualization.ipynb" && \
#    wget -q "https://bitbucket.org/yt_analysis/yt/raw/tip/doc/source/quickstart/4)_Data_Objects_and_Time_Series.ipynb" && \
#    wget -q "https://bitbucket.org/yt_analysis/yt/raw/tip/doc/source/quickstart/5)_Derived_Fields_and_Profiles.ipynb" && \
#    wget -q "https://bitbucket.org/yt_analysis/yt/raw/tip/doc/source/quickstart/6)_Volume_Rendering.ipynb" && \
#    wget -q https://bitbucket.org/data-exp-lab/galaxy-demo/raw/tip/galaxy_visualization.ipynb && \
#    wget -q https://bitbucket.org/data-exp-lab/galaxy-demo/raw/tip/field_names_map.json && \
#    wget -q https://bitbucket.org/data-exp-lab/galaxy-demo/raw/tip/field_types.json && \
#    wget -q https://bitbucket.org/data-exp-lab/galaxy-demo/raw/tip/num_images_map.json && \
#    wget -q https://bitbucket.org/data-exp-lab/galaxy-demo/raw/tip/sim_to_image_filenames.json && \
#    chmod 644 *.ipynb
#RUN sed -e 's/"python3"/"py3-stable"/g' -i *.ipynb 
#RUN sed -e '28,59d' -i /home/jovyan/work/1\)_Introduction.ipynb
