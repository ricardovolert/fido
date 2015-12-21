FROM node
RUN npm install -g slack-irc
VOLUME /tmp/config
CMD ["slack-irc", "-c", "/tmp/config/config.json"]
