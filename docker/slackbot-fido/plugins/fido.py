from __future__ import print_function
from rtmbot.core import Plugin
import logging
from .bb import FIDO_COMMANDS


class FidoPlugin(Plugin):

    def process_message(self, data):
        if 'text' not in data:
            return

        me = data.get('username') == 'yt-fido'
        bot_message = data.get('subtype') == 'bot_message'
        if me or bot_message:
            logging.info("Won't talk to bots")
            return

        outputs = self.outputs
        for command in FIDO_COMMANDS:
            command(data, outputs)
