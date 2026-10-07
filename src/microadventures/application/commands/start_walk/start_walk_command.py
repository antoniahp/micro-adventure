from dataclasses import dataclass
from uuid import UUID

from microadventures.domain.models.mood import Mood


@dataclass(frozen=True)
class StartWalkCommand:
    walk_id: UUID
    user_id: str
    mood: Mood
    minutes: int
    weather: str
    challenges_count: int
    note: str = ""
