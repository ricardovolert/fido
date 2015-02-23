FROM xarthisius/gentoo

MAINTAINER xarthisius.kk@gmail.com

#RUN echo 'PORTAGE_BINHOST="http://hub.yt/binhost/"' >> /etc/portage/make.conf && \
#    echo 'FEATURES="${FEATURES} getbinpkg"' >> /etc/portage/make.conf

RUN emerge-webrsync && \
    USE="-cxx romio mpi notebook cairo lapack" emerge -1v =ipython-2.2.0 =matplotlib-1.4.0 =numpy-1.8.2 \
    	"<mercurial-3.3" dev-python/nose cython sympy h5py mpi4py && \
    rm -rf /usr/portage/*

ONBUILD RUN cd /tmp && \
    hg clone https://bitbucket.org/yt_analysis/yt && \
    cd yt && \
    hg update -C yt

WORKDIR /tmp/yt
