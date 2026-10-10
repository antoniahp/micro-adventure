from dataclasses import dataclass

from microadventures.domain.models.challenge_category import ChallengeCategory


@dataclass(frozen=True)
class Sticker:
    code: str
    family: str  # what the sticker is about ("walks", "streak", "nature"...): the app words and draws it from this
    metric: str  # one of WalkHistory.metrics()
    goal: int


@dataclass(frozen=True)
class StickerProgress:
    code: str
    family: str
    current: int  # never above the goal, so a bar can always be drawn from it
    goal: int
    unlocked: bool


def _ladder(family: str, metric: str, goals: dict[int, str]) -> list[Sticker]:
    """One sticker per goal. The goals that already had a name in the first notebook keep it."""
    return [Sticker(code or f"{family}_{goal}", family, metric, goal) for goal, code in goals.items()]


# The goals are public: the notebook shows every sticker, with how far the person is from it.
CATALOG = tuple(
    _ladder("walks", "walks", {3: "", 5: "five_walks", 10: "", 20: "twenty_walks", 30: "", 50: "", 75: "", 100: ""})
    + _ladder("challenges", "challenges", {1: "first_walk", 10: "", 25: "", 50: "fifty_challenges", 100: "", 150: "", 250: "", 500: ""})
    + _ladder("perfect", "perfect_walks", {1: "perfect_walk", 3: "", 5: "", 10: "", 25: ""})
    + _ladder("streak", "streak", {2: "", 3: "streak_3", 5: "", 7: "streak_7", 10: "", 14: "", 30: ""})
    + _ladder("km", "km", {5: "", 10: "ten_km", 25: "", 50: "", 100: "", 200: ""})
    + _ladder("minutes", "minutes", {60: "", 300: "five_hours", 600: "", 1200: "", 3000: ""})
    + _ladder("stories", "stories", {3: "", 5: "", 10: "storyteller", 25: "", 50: ""})
    + _ladder("categories", "categories", {3: "", 5: "all_categories"})
    + [
        Sticker(f"{category.value}_{goal}", category.value, f"category_{category.value}", goal)
        for category in ChallengeCategory
        for goal in (5, 15, 30)
    ]
)


def sticker_book(metrics: dict[str, int]) -> list[StickerProgress]:
    book = []
    for sticker in CATALOG:
        value = metrics.get(sticker.metric, 0)
        book.append(StickerProgress(sticker.code, sticker.family, min(value, sticker.goal), sticker.goal, value >= sticker.goal))
    return book
