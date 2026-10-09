import requests

from microadventures.domain.exceptions.notification_failed_exception import NotificationFailedException
from microadventures.domain.models.reminder_card import ReminderCard
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

    def send_card(self, chat_id: str, card: ReminderCard) -> None:
        keyboard = {"inline_keyboard": _buttons(card)}
        try:
            self._call("sendPhoto", {"chat_id": chat_id, "photo": card.photo_url, "caption": card.caption, "parse_mode": "HTML", "reply_markup": keyboard})
        except NotificationFailedException:
            # Telegram could not get the picture (or refused it): the same message without it still reminds.
            self._call("sendMessage", {"chat_id": chat_id, "text": card.caption, "parse_mode": "HTML", "disable_web_page_preview": True, "reply_markup": keyboard})

    def answer(self, callback_id: str, text: str) -> None:
        self._call("answerCallbackQuery", {"callback_query_id": callback_id, "text": text})

    def register(self, url: str, secret: str) -> None:
        self._call("setWebhook", {"url": url, "secret_token": secret, "allowed_updates": ["message", "callback_query"]})

    def _call(self, method: str, body: dict) -> None:
        try:
            response = self.http.post(f"https://api.telegram.org/bot{self.token}/{method}", json=body, timeout=self.timeout_seconds)
        except requests.RequestException as error:
            # The error text can contain the URL, which holds the bot token: never pass it on.
            raise NotificationFailedException(type(error).__name__)
        if response.status_code != 200:
            raise NotificationFailedException(f"Telegram answered {response.status_code}")


def _buttons(card: ReminderCard) -> list[list[dict]]:
    rows = []
    if card.open_url:
        rows.append([{"text": card.open_label, "url": card.open_url}])
    rows.append([{"text": card.snooze_label, "callback_data": "snooze"}, {"text": card.skip_label, "callback_data": "skip"}])
    return rows
