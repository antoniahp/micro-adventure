from dataclasses import dataclass

from microadventures.domain.models.challenge_category import ChallengeCategory
from microadventures.domain.models.conditions import Conditions
from microadventures.domain.models.language import Language
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
    language: Language = Language.ES
    conditions: Conditions = Conditions()  # darkness, rain, cold...: what makes some challenges unsafe
