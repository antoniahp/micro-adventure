from uuid import UUID, uuid4

from django.db import models
from django.utils import timezone
from django_mongodb_backend.fields import EmbeddedModelArrayField

from microadventures.domain.models.challenge import Challenge
from microadventures.domain.models.challenge_status import ChallengeStatus
from microadventures.domain.exceptions.challenge_already_completed_exception import ChallengeAlreadyCompletedException
from microadventures.domain.exceptions.challenge_not_found_exception import ChallengeNotFoundException
from microadventures.domain.exceptions.swap_limit_reached_exception import SwapLimitReachedException
from microadventures.domain.models.language import Language
from microadventures.domain.models.mood import Mood

MAX_SWAPS_PER_WALK = 2


class Walk(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4)
    user_id = models.CharField(max_length=100, db_index=True)
    mood = models.CharField(max_length=20, choices=Mood.choices)
    minutes = models.PositiveSmallIntegerField()
    weather = models.CharField(max_length=50)
    note = models.CharField(max_length=500, blank=True, default="")
    language = models.CharField(max_length=5, choices=Language.choices, default=Language.ES)
    swaps_used = models.PositiveSmallIntegerField(default=0)
    challenges = EmbeddedModelArrayField(Challenge)
    created_at = models.DateTimeField(default=timezone.now)

    def find_challenge(self, challenge_id: UUID) -> Challenge:
        for challenge in self.challenges:
            if challenge.id == challenge_id:
                return challenge
        raise ChallengeNotFoundException(self.id, challenge_id)

    def complete_challenge(self, challenge_id: UUID, story: str = "") -> None:
        challenge = self.find_challenge(challenge_id)
        challenge.status = ChallengeStatus.COMPLETED
        challenge.story = story

    def ensure_can_swap(self, challenge_id: UUID) -> None:
        if self.find_challenge(challenge_id).is_completed:
            raise ChallengeAlreadyCompletedException(challenge_id)
        if self.swaps_used >= MAX_SWAPS_PER_WALK:
            raise SwapLimitReachedException(self.id)

    def swap_challenge(self, challenge_id: UUID, replacement: Challenge) -> None:
        self.ensure_can_swap(challenge_id)
        current = self.find_challenge(challenge_id)
        self.challenges[self.challenges.index(current)] = replacement
        self.swaps_used += 1

    @property
    def is_perfect(self) -> bool:
        """Every challenge completed without swapping any of them."""
        return bool(self.challenges) and self.swaps_used == 0 and all(c.is_completed for c in self.challenges)

    def __str__(self):
        return f"{self.user_id} · {self.created_at:%Y-%m-%d}"
