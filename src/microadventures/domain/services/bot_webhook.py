from abc import ABC, abstractmethod


class BotWebhook(ABC):
    """Tells the chat service where to send what people write to the bot."""

    @abstractmethod
    def register(self, url: str, secret: str) -> None:
        raise NotImplementedError
