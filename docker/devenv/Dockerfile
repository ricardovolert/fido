FROM xarthisius/gentoo

MAINTAINER xarthisius.kk@gmail.com

#RUN echo 'PORTAGE_BINHOST="http://hub.yt/binhost/"' >> /etc/portage/make.conf && \
#    echo 'FEATURES="${FEATURES} getbinpkg"' >> /etc/portage/make.conf

RUN emerge-webrsync && \
    echo "media-video/libav threads x264 vpx" >> /etc/portage/package.use && \
    echo "dev-vcs/git -perl -gpg -webdav" >> /etc/portage/package.use && \
    CPPFLAGS="-DNDEBUG" CFLAGS="-O2 -pipe" CXXFLAGS="-O2 -pipe"  USE="-cxx romio mpi notebook cairo lapack nbconvert -bindist" \
        emerge -1kv ipython matplotlib numpy pytables dev-libs/openssl openssh dev-vcs/git media-video/libav dev-python/numpydoc \
    	"<mercurial-3.3" dev-python/nose "<cython-0.22" sympy h5py mpi4py astropy pyregion scipy gsl dev-python/hglib && \
    rm -rf /usr/portage/*

ENV PYTHONPATH=/tmp/yt

RUN chmod go+rwx /tmp && \
    groupadd -g 1000 fido && \
    useradd -g 1000 -G 1000 -u 1000 -s /bin/bash fido

ADD ./SZpack.v1.1.1.tar.gz /tmp
ADD ./other_deps.sh /usr/local/bin/other_deps.sh
RUN bash /usr/local/bin/other_deps.sh

USER fido

ONBUILD RUN cd /tmp && \
    hg clone https://bitbucket.org/yt_analysis/yt && \
    cd yt && \
    hg update -C yt

#WORKDIR /tmp/yt
