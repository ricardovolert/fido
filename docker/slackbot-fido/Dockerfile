FROM jfloff/alpine-python:2.7-onbuild

ADD ./plugins /srv/app/plugins
ADD ./rtmbot.conf /srv/app/rtmbot.conf

WORKDIR /srv/app

CMD rtmbot
