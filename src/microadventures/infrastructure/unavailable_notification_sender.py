from microadventures.domain.exceptions.notification_unavailable_exception import NotificationUnavailableException
from microadventures.domain.models.reminder_card import ReminderCard
from microadventures.domain.services.bot_webhook import BotWebhook
from microadventures.domain.services.notification_sender import NotificationSender


class UnavailableNotificationSender(NotificationSender, BotWebhook):
    """Used when there is no bot token: the app works, it just cannot send reminders."""

    def send(self, chat_id: str, text: str) -> None:
        raise NotificationUnavailableException()

    def send_card(self, chat_id: str, card: ReminderCard) -> None:
        raise NotificationUnavailableException()

    def answer(self, callback_id: str, text: str) -> None:
        raise NotificationUnavailableException()

    def register(self, url: str, secret: str) -> None:
        raise NotificationUnavailableException()
