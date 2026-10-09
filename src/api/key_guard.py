import hashlib
import hmac

from django.conf import settings
from ninja.errors import HttpError


def check_key(key: str) -> None:
    """The calls that only we make (the clock, the one-time setup) carry the REMINDERS_KEY."""
    if not settings.REMINDERS_KEY:
        raise HttpError(503, "REMINDERS_KEY is not set")
    if not hmac.compare_digest(key.encode(), settings.REMINDERS_KEY.encode()):
        raise HttpError(403, "Wrong key")


def webhook_secret() -> str:
    """What Telegram sends back in a header, so we know a message really comes from it. Derived from the key."""
    return hashlib.sha256(f"telegram:{settings.REMINDERS_KEY}".encode()).hexdigest()
