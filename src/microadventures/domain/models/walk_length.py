from dataclasses import dataclass

SHORT_WALK_MINUTES = 45   # below this, the walk is short: 3 simple challenges
MEDIUM_WALK_MINUTES = 60  # from here on, the person chooses how many


@dataclass(frozen=True)
class WalkLength:
    """How many challenges a walk can have, given the time the person has.

    Less than 45 minutes: 3 simple ones. 45 to 59: 5. An hour or more: from 6 to 10, their choice.
    """

    minimum: int
    maximum: int
    default: int

    @classmethod
    def for_minutes(cls, minutes: int) -> "WalkLength":
        if minutes < SHORT_WALK_MINUTES:
            return cls(minimum=3, maximum=3, default=3)
        if minutes < MEDIUM_WALK_MINUTES:
            return cls(minimum=5, maximum=5, default=5)
        return cls(minimum=6, maximum=10, default=6)

    @property
    def is_short(self) -> bool:
        return self.maximum <= 3

    def accepts(self, count: int) -> bool:
        return self.minimum <= count <= self.maximum
