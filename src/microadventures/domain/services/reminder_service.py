from abc import ABC, abstractmethod

from microadventures.domain.models.reminder_settings import ReminderSettings


class ReminderService(ABC):
    @abstractmethod
    def save(self, settings: ReminderSettings) -> None:
        raise NotImplementedError

    @abstractmethod
    def find_by_user_id(self, user_id: str) -> ReminderSettings | None:
        raise NotImplementedError

    @abstractmethod
    def find_by_link_code(self, code: str) -> ReminderSettings | None:
        raise NotImplementedError

    @abstractmethod
    def find_by_telegram_chat_id(self, chat_id: str) -> ReminderSettings | None:
        raise NotImplementedError

    @abstractmethod
    def find_active(self) -> list[ReminderSettings]:
        """Everyone with reminders on and Telegram connected."""
        raise NotImplementedError
