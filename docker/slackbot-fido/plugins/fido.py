from __future__ import print_function
from rtmbot.core import Plugin
import logging
from .bb import FIDO_COMMANDS


class FidoPlugin(Plugin):

    def process_message(self, data):
        if 'text' not in data:
            return
        try:
            username = data['username']
            if username == 'yt-fido' or username.startswith('RatThing'):
                logging.info("Won't talk to myself")
                return
        except KeyError:
            pass

        outputs = self.outputs
        for command in FIDO_COMMANDS:
            command(data, outputs)
