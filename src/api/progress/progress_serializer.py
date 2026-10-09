from ninja import Schema


class ProgressOut(Schema):
    walks_count: int
    days_walked: int
    challenges_completed: int
    perfect_walks: int
    stickers: list[str]
