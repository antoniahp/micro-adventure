from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from microadventures.domain.models.language import Language
from microadventures.domain.models.mood import Mood


@dataclass(frozen=True)
class StartWalkCommand:
    walk_id: UUID
    user_id: str
    mood: Mood
    minutes: int
    weather: str
    challenges_count: int | None = None  # None: the usual number for that much time (WalkLength)
    note: str = ""
    language: Language = Language.ES
    latitude: float | None = None  # where the person is, when they allow it: the weather adapts the challenges
    longitude: float | None = None
    now: datetime | None = None
