from microadventures.domain.exceptions.notification_unavailable_exception import NotificationUnavailableException
from microadventures.domain.services.bot_webhook import BotWebhook
from microadventures.domain.services.notification_sender import NotificationSender


class UnavailableNotificationSender(NotificationSender, BotWebhook):
    """Used when there is no bot token: the app works, it just cannot send reminders."""

    def send(self, chat_id: str, text: str) -> None:
        raise NotificationUnavailableException()

    def register(self, url: str, secret: str) -> None:
        raise NotificationUnavailableException()
