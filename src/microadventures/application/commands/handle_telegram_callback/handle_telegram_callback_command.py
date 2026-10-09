from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class HandleTelegramCallbackCommand:
    chat_id: str
    callback_id: str
    data: str  # "snooze" or "skip": the buttons of the reminder
    now: datetime
