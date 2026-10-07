from uuid import uuid4

from django.db import models
from django_mongodb_backend.models import EmbeddedModel

from microadventures.domain.models.challenge_category import ChallengeCategory
from microadventures.domain.models.challenge_status import ChallengeStatus


class Challenge(EmbeddedModel):
    """Stored inside its walk, not in a collection of its own."""

    id = models.UUIDField(primary_key=True, default=uuid4)
    category = models.CharField(max_length=50, choices=ChallengeCategory.choices)
    text = models.CharField(max_length=300)
    status = models.CharField(max_length=20, choices=ChallengeStatus.choices, default=ChallengeStatus.PENDING)
    story = models.TextField(blank=True, default="")  # what the person told about it, written or transcribed from a voice note

    @property
    def accepts_photo(self) -> bool:
        # People are observed, never photographed. Those challenges are answered by telling.
        return self.category != ChallengeCategory.PEOPLE_WATCHING

    @property
    def is_completed(self) -> bool:
        return self.status == ChallengeStatus.COMPLETED

    def __str__(self):
        return self.text
