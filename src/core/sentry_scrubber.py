"""Keeps secrets out of what Sentry stores.

Telegram wants its token inside the URL (https://api.telegram.org/bot<token>/sendMessage), and the reminders
clock sends its key in the query string. Sentry records both URLs, so every event is cleaned before it leaves.
"""

import re

PATTERNS = (
    (re.compile(r"(bot\d+:)[\w-]+"), r"\1[Filtered]"),
    (re.compile(r"([?&]key=)[^&\s\"']+"), r"\1[Filtered]"),
)


def scrub_text(text: str) -> str:
    for pattern, replacement in PATTERNS:
        text = pattern.sub(replacement, text)
    return text


def scrub(value):
    if isinstance(value, str):
        return scrub_text(value)
    if isinstance(value, dict):
        return {key: scrub(item) for key, item in value.items()}
    if isinstance(value, list):
        return [scrub(item) for item in value]
    if isinstance(value, tuple):
        return tuple(scrub(item) for item in value)
    return value


def before_send(event, hint):
    """Used for errors and for traces (their spans hold the outgoing URLs)."""
    return scrub(event)
