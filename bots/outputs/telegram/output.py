"""
SPDX-FileCopyrightText: 2021 Jeremías Pretto - Mateo Durante
SPDX-License-Identifier: AGPL-3.0-or-later

Example Output Bot for Telemgram Demo purpose only.

Document possible necessary configurations.
"""
import telebot

import intelmq.lib.utils as utils
from intelmq.lib.bot import OutputBot
from intelmq.lib.exceptions import MissingDependencyError


class TelegramOutputBot(OutputBot):
    """Send events to a REST API listener through HTTP POST"""
    token: str = None
    chat_id: str = None
    message: str = None
    parse_mode: str = None
    disable_web_page_preview: bool = False

    def init(self):
        self.bot = telebot.TeleBot(self.token, parse_mode=None)


    def process(self):
        event = self.receive_message()
        self.bot.send_message(self.chat_id,  self.message.format(ev=event), parse_mode=self.parse_mode, disable_web_page_preview=self.disable_web_page_preview)
        self.acknowledge_message()




BOT = TelegramOutputBot

