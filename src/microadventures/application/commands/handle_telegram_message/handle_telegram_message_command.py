from dataclasses import dataclass


@dataclass(frozen=True)
class HandleTelegramMessageCommand:
    chat_id: str
    text: str  # "/start <code>", "/stop", or anything else
