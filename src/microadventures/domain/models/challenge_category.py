from django.db import models


class ChallengeCategory(models.TextChoices):
    SENSORY = "sensory"
    SOUND = "sound"
    CULTURE = "culture"
    NATURE = "nature"
    PEOPLE_WATCHING = "people_watching"
