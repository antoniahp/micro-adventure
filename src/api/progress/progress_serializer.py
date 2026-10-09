from ninja import Schema


class StickerOut(Schema):
    code: str
    current: int
    goal: int
    unlocked: bool


class ProgressOut(Schema):
    walks_count: int
    days_walked: int
    challenges_completed: int
    perfect_walks: int
    stickers: list[str]  # the codes already earned
    sticker_book: list[StickerOut]  # every sticker, with how far the person is from it
    current_streak: int
