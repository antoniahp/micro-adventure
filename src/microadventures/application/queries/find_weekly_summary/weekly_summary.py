from dataclasses import dataclass, field
from datetime import date


@dataclass(frozen=True)
class DaySummary:
    day: date
    walks: int
    challenges: int


@dataclass(frozen=True)
class WeeklySummary:
    week_start: date  # Monday
    week_end: date  # Sunday
    walks_count: int
    days_walked: int
    challenges_completed: int
    perfect_walks: int
    minutes: int
    km: float
    stories: int
    days: list[DaySummary] = field(default_factory=list)
    moods: dict[str, int] = field(default_factory=dict)
    categories: dict[str, int] = field(default_factory=dict)
    previous_walks: int = 0
    previous_challenges: int = 0
    previous_minutes: int = 0
    previous_km: float = 0.0
    feeling: int | None = None
    feeling_note: str = ""
