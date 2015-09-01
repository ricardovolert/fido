FROM xarthisius/gentoo

MAINTAINER xarthisius.kk@gmail.com

RUN echo 'PORTAGE_BINHOST="http://use.yt/gentoo/"' >> /etc/portage/make.conf && \
    echo 'FEATURES="${FEATURES} getbinpkg"' >> /etc/portage/make.conf && \
    echo 'CPU_FLAGS_X86="aes avx avx2 fma3 mmx mmxext popcnt sse sse2 sse3 sse4_1 sse4_2 ssse3"' >> /etc/portage/make.conf && \
    echo "media-video/libav openssl threads x264 vpx" >> /etc/portage/package.use && \
    echo "dev-vcs/git -perl -gpg -webdav" >> /etc/portage/package.use && \
    echo "sys-devel/gcc cxx" >> /etc/portage/package.use && \
    echo "sci-libs/hdf5 -cxx" >> /etc/portage/package.use && \
    echo "dev-python/sphinx latex" >> /etc/portage/package.use && \
    echo "dev-lang/python sqlite" >> /etc/portage/package.use && \
    echo "dev-lang/ghc binary" >> /etc/portage/package.use && \
    echo "media-libs/gd jpeg png" >> /etc/portage/package.use && \
    echo ">=app-text/ghostscript-gpl-9.15-r1 cups" >> /etc/portage/package.use && \
    echo ">=x11-libs/cairo-1.14.2 X" >> /etc/portage/package.use && \
    chown -R root:root /var/* && \
    mkdir -p /var/log/supervisor

ADD supervisord.conf /etc/supervisord.conf

RUN emerge-webrsync && \
    rm -rf /usr/lib64/misc/ssh-keysign /bin/mount /bin/umount && \
    CFLAGS="-O2 -pipe" CXXFLAGS="-O2 -pipe"  USE="romio mpi notebook cairo lapack nbconvert -bindist" \
        emerge -1uDNkv "<ipython-3.0.0" matplotlib numpy pytables dev-libs/openssl openssh dev-vcs/git media-video/libav \
    	mercurial dev-python/nose cython sympy h5py mpi4py astropy pyregion scipy gsl dev-python/hglib \
	dev-python/sphinx-bootstrap-theme dev-python/Babel dev-python/pygments dev-texlive/texlive-latexextra \
        app-text/dvipng cmake swig net-libs/http-parser =dev-libs/libuv-1.4.2 dev-python/wcsaxes =pyx-0.12.1-r1 \
	dev-python/numpydoc dev-java/icedtea-bin app-admin/supervisor freeglut imagemagick libXmu openexr && \
    rm -rf /usr/portage/*

RUN emerge-webrsync && \
    sed -i -e 's/getbinpkg//g' /etc/portage/make.conf && \
    emerge -1 app-text/pandoc && \
    emerge -C net-libs/nodejs && \
    rm -rf /usr/portage/*

ENV PYTHONPATH=/tmp/yt

RUN chmod go+rwx /tmp && \
    groupadd -g 1000 fido && \
    useradd -g 1000 -G 1000 -u 1000 -s /bin/bash fido

ADD ./SZpack.v1.1.1.tar.gz /tmp
ADD ./other_deps.sh /usr/local/bin/other_deps.sh
RUN bash /usr/local/bin/other_deps.sh

ADD ./nose.patch /tmp/nose.patch
RUN cd / && patch -p0 < /tmp/nose.patch

USER fido

ONBUILD RUN cd /tmp && \
    hg clone https://bitbucket.org/yt_analysis/yt && \
    cd yt && \
    echo "/usr/local/src/rockstar" > /tmp/yt/rockstar.cfg && \
    hg update -C yt

#WORKDIR /tmp/yt
