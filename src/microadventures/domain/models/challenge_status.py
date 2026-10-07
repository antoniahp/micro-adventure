from django.db import models


class ChallengeStatus(models.TextChoices):
    PENDING = "pending"
    COMPLETED = "completed"
