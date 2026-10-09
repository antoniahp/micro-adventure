import requests

from microadventures.domain.exceptions.notification_failed_exception import NotificationFailedException
from microadventures.domain.services.bot_webhook import BotWebhook
from microadventures.domain.services.notification_sender import NotificationSender


class TelegramNotificationSender(NotificationSender, BotWebhook):
    """Talks to a Telegram bot: https://core.telegram.org/bots/api"""

    def __init__(self, token: str, http=requests, timeout_seconds: int = 10):
        self.token = token
        self.http = http
        self.timeout_seconds = timeout_seconds

    def send(self, chat_id: str, text: str) -> None:
        self._call("sendMessage", {"chat_id": chat_id, "text": text, "disable_web_page_preview": True})

    def register(self, url: str, secret: str) -> None:
        self._call("setWebhook", {"url": url, "secret_token": secret, "allowed_updates": ["message"]})

    def _call(self, method: str, body: dict) -> None:
        try:
            response = self.http.post(f"https://api.telegram.org/bot{self.token}/{method}", json=body, timeout=self.timeout_seconds)
        except requests.RequestException as error:
            # The error text can contain the URL, which holds the bot token: never pass it on.
            raise NotificationFailedException(type(error).__name__)
        if response.status_code != 200:
            raise NotificationFailedException(f"Telegram answered {response.status_code}")
