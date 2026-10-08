from django.db import models


class Language(models.TextChoices):
    """Languages the app can write challenges in."""

    ES = "es"
    EN = "en"
