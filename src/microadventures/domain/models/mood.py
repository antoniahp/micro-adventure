from django.db import models


class Mood(models.TextChoices):
    TIRED = "tired"
    CALM = "calm"
    ACTIVE = "active"
