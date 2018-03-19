FROM jfloff/alpine-python:2.7-onbuild

ADD ./build-requirements.txt /build-requirements.txt
ADD ./plugins /srv/app/plugins
ADD ./rtmbot.conf /srv/app/rtmbot.conf

WORKDIR /srv/app

CMD rtmbot
