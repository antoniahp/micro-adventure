from dataclasses import dataclass, field

from microadventures.domain.models.sticker import StickerProgress


@dataclass(frozen=True)
class Progress:
    walks_count: int
    days_walked: int
    challenges_completed: int
    perfect_walks: int
    stickers: list[str] = field(default_factory=list)  # the codes already earned
    sticker_book: list[StickerProgress] = field(default_factory=list)  # all of them, with how far each one is
    current_streak: int = 0
