from ninja import Schema


class TelegramLinkOut(Schema):
    url: str


class TelegramUpdate(Schema):
    message: dict | None = None
