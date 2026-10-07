from dataclasses import dataclass, field


@dataclass(frozen=True)
class Progress:
    walks_count: int
    days_walked: int
    challenges_completed: int
    perfect_walks: int
    stickers: list[str] = field(default_factory=list)
