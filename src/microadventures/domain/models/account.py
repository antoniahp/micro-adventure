from uuid import uuid4

from django.db import models
from django.utils import timezone as django_timezone


class Account(models.Model):
    """The record that an anonymous user id already belongs to a device.

    There is no login: the first time a browser shows up, it gets a session for its id. Once an id is claimed,
    nobody else can start a session with it, so knowing someone's id is no longer enough to read their data.
    """

    id = models.UUIDField(primary_key=True, default=uuid4)
    user_id = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(default=django_timezone.now)

    # Both optional, added so nobody has to lose their walks and badges to get them: a name the person
    # chooses to be greeted by, and a Google identity that lets the same progress be found again from
    # another browser or after this one's local data is gone. google_sub is Google's own opaque id for
    # the account (not a readable personal detail, needed as-is to look the account back up); the email
    # is a real personal detail, so only its hash is kept (core/email_hash.py) — never the address itself.
    nickname = models.CharField(max_length=50, null=True, blank=True)
    google_sub = models.CharField(max_length=255, null=True, blank=True, db_index=True)
    google_email_hash = models.CharField(max_length=64, null=True, blank=True)
