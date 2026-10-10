"""Keeps secrets out of what Sentry stores and out of the logs Render shows.

Three layers, because a key can leak in different shapes:
1. Known shapes: the Telegram token in its URL, `?key=` in query strings, the user and password of a MongoDB
   address, and `Authorization: Bearer ...` headers.
2. Names: any dictionary field called api_key, authorization, password, token, cookie... is emptied.
3. Values: whatever the environment holds in a variable named like KEY, TOKEN, SECRET, PASSWORD, URI or DSN is
   replaced wherever it appears, even in a shape nobody foresaw.
"""

import logging
import os
import re

FILTERED = "[Filtered]"

PATTERNS = (
    (re.compile(r"(bot\d+:)[\w-]+"), rf"\1{FILTERED}"),
    (re.compile(r"([?&]key=)[^&\s\"']+"), rf"\1{FILTERED}"),
    (re.compile(r"(mongodb(?:\+srv)?://)[^/@\s]+@"), rf"\1{FILTERED}@"),
    (re.compile(r"(?i)\b(bearer\s+)[\w.~+/=-]+"), rf"\1{FILTERED}"),
    (re.compile(r"(?i)\b((?:xi-api-key|api[-_]?key|password|secret)['\"]?\s*[:=]\s*['\"]?)[^\s,'\"&}]+"), rf"\1{FILTERED}"),
)

SENSITIVE_NAMES = re.compile(r"(?i)(api[-_]?key|authorization|password|passwd|secret|token|cookie|credential|dsn)")
SECRET_ENV_NAMES = re.compile(r"(KEY|TOKEN|SECRET|PASSWORD|URI|DSN)")
MIN_SECRET_LENGTH = 8  # a short value would also cut up ordinary words


def secret_values() -> list[str]:
    """Read at every call, so a variable changed in the panel is covered after the restart without code changes."""
    values = {value for name, value in os.environ.items() if SECRET_ENV_NAMES.search(name) and len(value) >= MIN_SECRET_LENGTH}
    return sorted(values, key=len, reverse=True)  # the longest first: a URI contains the password inside


def scrub_text(text: str) -> str:
    for secret in secret_values():
        text = text.replace(secret, FILTERED)
    for pattern, replacement in PATTERNS:
        text = pattern.sub(replacement, text)
    return text


def scrub(value):
    if isinstance(value, str):
        return scrub_text(value)
    if isinstance(value, dict):
        return {key: FILTERED if isinstance(key, str) and SENSITIVE_NAMES.search(key) and item else scrub(item) for key, item in value.items()}
    if isinstance(value, list):
        return [scrub(item) for item in value]
    if isinstance(value, tuple):
        return tuple(scrub(item) for item in value)
    return value


def before_send(event, hint):
    """Used for errors and for traces (their spans hold the outgoing URLs)."""
    return scrub(event)


def before_send_log(log, hint):
    """Used for Sentry Logs: the message and its attributes can hold the same URLs."""
    return scrub(log)


class SecretsFilter(logging.Filter):
    """Cleans every console log line (what Render shows) before it is written."""

    def filter(self, record: logging.LogRecord) -> bool:
        record.msg = scrub_text(record.getMessage())
        record.args = None
        if record.exc_info and record.exc_info[1] is not None and not record.exc_text:
            record.exc_text = scrub_text(logging.Formatter().formatException(record.exc_info))
        elif record.exc_text:
            record.exc_text = scrub_text(record.exc_text)
        return True
