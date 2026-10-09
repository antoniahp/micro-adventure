import pytest
import requests

from microadventures.domain.exceptions.notification_failed_exception import NotificationFailedException
from microadventures.domain.exceptions.notification_unavailable_exception import NotificationUnavailableException
from microadventures.infrastructure.api.telegram_notification_sender import TelegramNotificationSender
from microadventures.infrastructure.unavailable_notification_sender import UnavailableNotificationSender


class FakeHttp:
    def __init__(self, status_code=200, error=None):
        self.status_code = status_code
        self.error = error
        self.requests = []

    def post(self, url, json, timeout):
        self.requests.append((url, json))
        if self.error:
            raise self.error
        return self


def test_telegram_sends_the_message_to_the_chat():
    http = FakeHttp()

    TelegramNotificationSender("123:TOKEN", http=http).send("555", "Hola")

    url, body = http.requests[0]
    assert url == "https://api.telegram.org/bot123:TOKEN/sendMessage"
    assert body["chat_id"] == "555" and body["text"] == "Hola"


def test_telegram_registers_the_webhook_with_the_secret():
    http = FakeHttp()

    TelegramNotificationSender("123:TOKEN", http=http).register("https://x/api/telegram/webhook", "s3cret")

    url, body = http.requests[0]
    assert url.endswith("/setWebhook")
    assert (body["url"], body["secret_token"]) == ("https://x/api/telegram/webhook", "s3cret")


def test_telegram_fails_when_it_answers_with_an_error():
    with pytest.raises(NotificationFailedException):
        TelegramNotificationSender("123:TOKEN", http=FakeHttp(status_code=403)).send("555", "Hola")


def test_the_error_never_contains_the_bot_token():
    # requests puts the whole URL, token included, in its error messages
    http = FakeHttp(error=requests.ConnectionError("failed to reach https://api.telegram.org/bot123:TOKEN/sendMessage"))

    with pytest.raises(NotificationFailedException) as raised:
        TelegramNotificationSender("123:TOKEN", http=http).send("555", "Hola")

    assert "TOKEN" not in str(raised.value)


def test_without_a_bot_the_sender_says_it_is_not_available():
    with pytest.raises(NotificationUnavailableException):
        UnavailableNotificationSender().send("555", "Hola")
    with pytest.raises(NotificationUnavailableException):
        UnavailableNotificationSender().register("https://x", "s")
