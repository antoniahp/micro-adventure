from dataclasses import dataclass


@dataclass(frozen=True)
class UnlinkTelegramCommand:
    user_id: str
