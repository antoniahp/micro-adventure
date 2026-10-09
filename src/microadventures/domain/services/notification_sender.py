from abc import ABC, abstractmethod


class NotificationSender(ABC):
    """Sends a short message to a person's chat. Telegram today; it could be another channel."""

    @abstractmethod
    def send(self, chat_id: str, text: str) -> None:
        raise NotImplementedError
