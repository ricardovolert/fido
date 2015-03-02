FROM xarthisius/gentoo

MAINTAINER xarthisius.kk@gmail.com

#RUN echo 'PORTAGE_BINHOST="http://hub.yt/binhost/"' >> /etc/portage/make.conf && \
#    echo 'FEATURES="${FEATURES} getbinpkg"' >> /etc/portage/make.conf

RUN emerge-webrsync && \
    USE="-cxx romio mpi notebook cairo lapack" emerge -1kv =ipython-2.2.0 =matplotlib-1.4.0 =numpy-1.8.2 \
    	"<mercurial-3.3" dev-python/nose "<cython-0.22" sympy h5py mpi4py astropy pyregion && \
    rm -rf /usr/portage/*

RUN mkdir -p /usr/local/src && \
    cd /usr/local/src && \
    hg clone https://bitbucket.org/MatthewTurk/rockstar && \
    cd rockstar && \
    hg update -C tip && \
    rm -rf .hg && \
    make lib && \
    cp librockstar.so /usr/lib64

ONBUILD RUN cd /tmp && \
    hg clone https://bitbucket.org/yt_analysis/yt && \
    cd yt && \
    hg update -C yt

WORKDIR /tmp/yt
