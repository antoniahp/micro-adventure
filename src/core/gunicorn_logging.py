"""gunicorn's access log writes the full URL, and the reminders clock puts its key in it (?key=...)."""

import logging

from gunicorn.glogging import Logger

from core.sentry_scrubber import SecretsFilter


class RedactingLogger(Logger):
    def setup(self, cfg):
        super().setup(cfg)
        self.access_log.addFilter(SecretsFilter())
        self.error_log.addFilter(SecretsFilter())
