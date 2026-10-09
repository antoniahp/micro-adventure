from abc import ABC, abstractmethod

from microadventures.domain.models.reminder_card import ReminderCard


class NotificationSender(ABC):
    """Sends messages to a person's chat. Telegram today; it could be another channel."""

    @abstractmethod
    def send(self, chat_id: str, text: str) -> None:
        raise NotImplementedError

    @abstractmethod
    def send_card(self, chat_id: str, card: ReminderCard) -> None:
        """A picture with a text and buttons. The buttons answer with 'snooze' or 'skip'."""
        raise NotImplementedError

    @abstractmethod
    def answer(self, callback_id: str, text: str) -> None:
        """Answers a button press with a small notice."""
        raise NotImplementedError
