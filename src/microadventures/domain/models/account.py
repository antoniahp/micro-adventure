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
