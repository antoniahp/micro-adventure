from dataclasses import dataclass


@dataclass(frozen=True)
class CreateTelegramLinkCommand:
    user_id: str
    link_code: str  # a random code; the person sends it to the bot to prove this chat is theirs
