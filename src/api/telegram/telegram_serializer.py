from ninja import Schema


class TelegramLinkOut(Schema):
    url: str


class TelegramUpdate(Schema):
    message: dict | None = None
    callback_query: dict | None = None  # a press on a button of the reminder
