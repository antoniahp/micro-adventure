from uuid import uuid4

from django.db import models
from django_mongodb_backend.models import EmbeddedModel

from microadventures.domain.models.challenge_category import ChallengeCategory
from microadventures.domain.models.challenge_status import ChallengeStatus


TEMPLATE_SOURCE = "template"  # any other value is the name of the model that wrote the challenge


class Challenge(EmbeddedModel):
    """Stored inside its walk, not in a collection of its own."""

    id = models.UUIDField(primary_key=True, default=uuid4)
    category = models.CharField(max_length=50, choices=ChallengeCategory.choices)
    text = models.CharField(max_length=300)
    status = models.CharField(max_length=20, choices=ChallengeStatus.choices, default=ChallengeStatus.PENDING)
    story = models.TextField(blank=True, default="")  # what the person told about it, written or transcribed from a voice note
    source = models.CharField(max_length=60, default=TEMPLATE_SOURCE)  # "template" or the model that wrote it, e.g. "gemma4:31b"

    @property
    def accepts_photo(self) -> bool:
        # People are observed, never photographed, and a sound cannot be seen: those challenges are answered by telling.
        return self.category not in (ChallengeCategory.PEOPLE_WATCHING, ChallengeCategory.SOUND)

    @property
    def written_by_model(self) -> bool:
        return self.source != TEMPLATE_SOURCE

    @property
    def is_completed(self) -> bool:
        return self.status == ChallengeStatus.COMPLETED

    def __str__(self):
        return self.text
