from dataclasses import dataclass

from microadventures.domain.models.challenge_category import ChallengeCategory
from microadventures.domain.models.mood import Mood


@dataclass(frozen=True)
class ChallengeBrief:
    """What a generator needs to know to create challenges for one walk."""

    mood: Mood
    minutes: int
    weather: str
    count: int
    category: ChallengeCategory | None = None
    note: str = ""  # what the person wrote about their day, in their own words
