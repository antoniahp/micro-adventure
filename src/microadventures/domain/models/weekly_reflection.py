from uuid import uuid4

from django.db import models
from django.utils import timezone

from microadventures.domain.exceptions.invalid_weekly_reflection_exception import InvalidWeeklyReflectionException

MAX_NOTE_LENGTH = 500


class WeeklyReflection(models.Model):
    """How the person says they felt during a week (Monday to Sunday). One per person and week."""

    id = models.UUIDField(primary_key=True, default=uuid4)
    user_id = models.CharField(max_length=100, db_index=True)
    week_start = models.DateField()  # the Monday
    feeling = models.PositiveSmallIntegerField()  # 1 (bad) to 5 (great)
    note = models.CharField(max_length=MAX_NOTE_LENGTH, blank=True, default="")
    updated_at = models.DateTimeField(default=timezone.now)

    def change(self, feeling: int, note: str) -> None:
        if not 1 <= feeling <= 5:
            raise InvalidWeeklyReflectionException("The feeling goes from 1 to 5.")
        self.feeling = feeling
        self.note = note.strip()[:MAX_NOTE_LENGTH]
        self.updated_at = timezone.now()

    def __str__(self):
        return f"{self.user_id} · {self.week_start} · {self.feeling}"
