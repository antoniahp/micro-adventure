from dataclasses import dataclass


@dataclass(frozen=True)
class RegisterBotWebhookCommand:
    url: str
    secret: str
