# SPDX-FileCopyrightText: 2024
#
# SPDX-License-Identifier: AGPL-3.0-or-later

# -*- coding: utf-8 -*-
from typing import Iterable

try:
    import requests
except ImportError:
    requests = None

import intelmq.lib.utils as utils
from intelmq.lib.bot import OutputBot
from intelmq.lib.exceptions import MissingDependencyError


class CTFdOutputBot(OutputBot):
    """Send events to a CTFD instance through HTTP POST"""
    auth_token_name: str = "Authorization"
    auth_token: str = None
    auth_type = str = "http_header"
    hierarchical_output: bool = False
    host: str = "https://ctfd-intelmq.taller.org/api/v1/challenges/attempt"
    use_json: bool = False
    challenge_id = "extra.challenge_id"
    challenge_submission = "extra.submission"

    _auth: Iterable[str] = None

    def init(self):
        if requests is None:
            raise MissingDependencyError("requests")

        self.set_request_parameters()

        if self.auth_token_name and self.auth_token:
            if self.auth_type == 'http_header':
                self.http_header.update(
                    {self.auth_token_name: self.auth_token})
            elif self.auth_type == 'http_basic_auth':
                self.auth = self.auth_token_name, self.auth_token
        # We fix this because CTFD bug -> https://github.com/CTFd/CTFd/pull/2564
        self.http_header.update({"Content-Type":
                                 "application/json"})

        self.session = utils.create_request_session(self)
        self.session.keep_alive = False

    def process(self):
        event = self.receive_message()
        self.logger.info(f'Recieving event: {str(event)}')
        kwargs={'json': { 'challenge_id': int(event.get(self.challenge_id,0)),'submission':event.get(self.challenge_submission,'ERROR')} }
        self.logger.info(f'Sending data: {str(kwargs)}')
        timeoutretries = 0
        req = None
        while timeoutretries < self.http_timeout_max_tries and req is None:
            try:
                req = self.session.post(self.host,
                                        timeout=self.http_timeout_sec,
                                        **kwargs)
            except requests.exceptions.Timeout:
                timeoutretries += 1

        if req is None and timeoutretries >= self.http_timeout_max_tries:
            raise ValueError("Request timed out %i times in a row."
                             "" % timeoutretries)

        if not req.ok:
            self.logger.debug("Error during message sending, response body: %r.",
                              req.text)
            
        req.raise_for_status()
        self.logger.info(f'Sent message {req.text}')
        self.acknowledge_message()


BOT = CTFdOutputBot
