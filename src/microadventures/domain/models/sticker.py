from dataclasses import dataclass


@dataclass(frozen=True)
class Sticker:
    code: str
    metric: str  # one of WalkHistory.metrics()
    goal: int


@dataclass(frozen=True)
class StickerProgress:
    code: str
    current: int  # never above the goal, so a bar can always be drawn from it
    goal: int
    unlocked: bool


# The goals are public: the notebook shows every sticker, with how far the person is from it.
CATALOG = (
    Sticker("first_walk", "challenges", 1),
    Sticker("perfect_walk", "perfect_walks", 1),
    Sticker("five_walks", "walks", 5),
    Sticker("twenty_walks", "walks", 20),
    Sticker("fifty_challenges", "challenges", 50),
    Sticker("all_categories", "categories", 5),
    Sticker("streak_3", "streak", 3),
    Sticker("streak_7", "streak", 7),
    Sticker("storyteller", "stories", 10),
    Sticker("ten_km", "km", 10),
    Sticker("five_hours", "minutes", 300),
)


def sticker_book(metrics: dict[str, int]) -> list[StickerProgress]:
    book = []
    for sticker in CATALOG:
        value = metrics.get(sticker.metric, 0)
        book.append(StickerProgress(sticker.code, min(value, sticker.goal), sticker.goal, value >= sticker.goal))
    return book
