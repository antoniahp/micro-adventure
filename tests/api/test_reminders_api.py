import hashlib
import json

import pytest
from tests.auth_helpers import signed_in

from api import wiring
from tests.fakes import InMemoryAccountRepository, InMemoryReminderRepository, InMemoryWalkRepository, SpyNotificationSender
from microadventures.infrastructure.template_challenge_generator import TemplateChallengeGenerator

KEY = "clock-key"
SECRET = hashlib.sha256(f"telegram:{KEY}".encode()).hexdigest()


@pytest.fixture(autouse=True)
def adapters(monkeypatch, settings):
    walks, reminders, sender = InMemoryWalkRepository(), InMemoryReminderRepository(), SpyNotificationSender()
    accounts = InMemoryAccountRepository()
    monkeypatch.setattr(wiring, "_walk_repository", lambda: walks)
    monkeypatch.setattr(wiring, "_challenge_generator", lambda: TemplateChallengeGenerator())
    monkeypatch.setattr(wiring, "_reminder_repository", lambda: reminders)
    monkeypatch.setattr(wiring, "_notification_sender", lambda: sender)
    monkeypatch.setattr(wiring, "_account_repository", lambda: accounts)
    settings.REMINDERS_KEY = KEY
    settings.TELEGRAM_BOT_TOKEN = "123:TOKEN"
    settings.TELEGRAM_BOT_USERNAME = "MicroAdventuresBot"
    settings.APP_URL = "https://micro-adventure.onrender.com"
    return {"reminders": reminders, "sender": sender, "accounts": accounts}


def _put(client, user, body):
    return client.put(f"/api/users/{user}/reminders", data=json.dumps(body), content_type="application/json")


def _webhook(client, text, chat_id=999, secret=SECRET):
    body = {"update_id": 1, "message": {"chat": {"id": chat_id}, "text": text}}
    return client.post("/api/telegram/webhook", data=json.dumps(body), content_type="application/json", HTTP_X_TELEGRAM_BOT_API_SECRET_TOKEN=secret)


def test_someone_new_gets_the_defaults_switched_off():
    body = signed_in().get("/api/users/user-1/reminders").json()

    assert body == {
        "enabled": False, "weekday_time": "18:00", "weekend_time": "11:00", "timezone": "Europe/Madrid",
        "language": "es", "telegram_connected": False, "has_place": False, "telegram_available": True,
    }


def test_the_app_knows_when_the_server_has_no_bot(settings):
    settings.TELEGRAM_BOT_TOKEN = ""

    assert signed_in().get("/api/users/user-1/reminders").json()["telegram_available"] is False


def test_the_settings_are_saved():
    client = signed_in()

    saved = _put(client, "user-1", {"enabled": True, "weekday_time": "19:15", "weekend_time": "10:00", "timezone": "Europe/London", "language": "en"})

    assert saved.status_code == 200
    assert client.get("/api/users/user-1/reminders").json()["weekday_time"] == "19:15"


def test_a_wrong_time_or_time_zone_is_refused():
    client = signed_in()
    ok = {"enabled": True, "weekday_time": "18:00", "weekend_time": "11:00", "timezone": "Europe/Madrid"}

    assert _put(client, "user-1", {**ok, "weekday_time": "late"}).status_code == 422
    assert _put(client, "user-1", {**ok, "timezone": "Mars/Olympus"}).status_code == 422


def test_connecting_telegram_end_to_end(adapters):
    client = signed_in()

    link = client.post("/api/users/user-1/telegram/link").json()["url"]
    code = link.split("?start=")[1]
    assert link.startswith("https://t.me/MicroAdventuresBot?start=")

    assert _webhook(client, f"/start {code}").status_code == 204

    assert client.get("/api/users/user-1/reminders").json()["telegram_connected"] is True
    assert adapters["sender"].sent[0][0] == "999"


def test_connecting_needs_a_bot_on_the_server(settings):
    settings.TELEGRAM_BOT_USERNAME = ""

    assert signed_in().post("/api/users/user-1/telegram/link").status_code == 503


def test_the_person_can_disconnect():
    client = signed_in()
    code = client.post("/api/users/user-1/telegram/link").json()["url"].split("?start=")[1]
    _webhook(client, f"/start {code}")

    assert client.delete("/api/users/user-1/telegram").status_code == 204

    assert client.get("/api/users/user-1/reminders").json()["telegram_connected"] is False


def test_the_webhook_refuses_messages_without_the_secret():
    assert _webhook(signed_in(), "/start x", secret="wrong").status_code == 403
    assert _webhook(signed_in(), "/start x", secret="").status_code == 403


def test_the_webhook_ignores_updates_without_a_text_message(adapters):
    body = {"update_id": 2, "edited_message": {"chat": {"id": 1}, "text": "x"}}

    response = signed_in().post("/api/telegram/webhook", data=json.dumps(body), content_type="application/json", HTTP_X_TELEGRAM_BOT_API_SECRET_TOKEN=SECRET)

    assert response.status_code == 204 and adapters["sender"].sent == []


def test_the_setup_registers_the_webhook_with_the_secret(adapters):
    response = signed_in().post(f"/api/telegram/setup?key={KEY}")

    assert response.status_code == 204
    assert adapters["sender"].registered == [("https://micro-adventure.onrender.com/api/telegram/webhook", SECRET)]


def test_the_calls_only_the_clock_makes_need_the_key(settings):
    client = signed_in()

    assert client.post("/api/reminders/run?key=wrong").status_code == 403
    assert client.post("/api/telegram/setup?key=wrong").status_code == 403
    settings.REMINDERS_KEY = ""
    assert client.post("/api/reminders/run?key=").status_code == 503


def test_the_clock_sends_the_reminders_that_are_due(adapters, monkeypatch):
    from datetime import datetime, timezone
    from api.reminders import reminders_view as telegram_router

    client = signed_in()
    _put(client, "user-1", {"enabled": True, "weekday_time": "18:00", "weekend_time": "11:00", "timezone": "Europe/Madrid"})
    code = client.post("/api/users/user-1/telegram/link").json()["url"].split("?start=")[1]
    _webhook(client, f"/start {code}")
    adapters["sender"].sent.clear()

    class Friday1830:
        @staticmethod
        def now(tz):
            return datetime(2026, 10, 9, 16, 30, tzinfo=tz)

    monkeypatch.setattr(telegram_router, "datetime", Friday1830)

    assert client.post(f"/api/reminders/run?key={KEY}").json() == {"sent": 1}
    assert client.post(f"/api/reminders/run?key={KEY}").json() == {"sent": 0}
    assert "Tu jornada ha terminado" in adapters["sender"].cards[0][1].caption
