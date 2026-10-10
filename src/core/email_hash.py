"""Turns an email address into a one-way hash before it ever reaches storage.

Keyed with the app's own secret (HMAC, not plain SHA-256) so a leaked database can't be matched
against a dictionary of common addresses without also having DJANGO_SECRET_KEY. The hash is never
turned back into an email anywhere in this app — it exists only so the server can recognise "this
is the same Google account as before", not to display or recover the address.
"""

import hashlib
import hmac

from django.conf import settings


def hash_email(email: str) -> str:
    normalized = email.strip().lower()
    return hmac.new(settings.SECRET_KEY.encode(), normalized.encode(), hashlib.sha256).hexdigest()
