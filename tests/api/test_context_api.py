import json
from uuid import UUID

import pytest
from tests.auth_helpers import signed_in

from api import wiring
from tests.fakes import FakeWeatherService, InMemoryReminderRepository, InMemoryWalkRepository, SpyNotificationSender
from tests.microadventures.object_mothers import a_reminder, a_weather
from microadventures.domain.models.weather import Sky
from microadventures.infrastructure.template_challenge_generator import TemplateChallengeGenerator
import hashlib

KEY = "clock-key"
SECRET = hashlib.sha256(f"telegram:{KEY}".encode()).hexdigest()


@pytest.fixture
def adapters(monkeypatch, settings):
    walks, reminders, sender = InMemoryWalkRepository(), InMemoryReminderRepository(), SpyNotificationSender()
    weather = FakeWeatherService(a_weather(sky=Sky.RAIN))
    monkeypatch.setattr(wiring, "_walk_repository", lambda: walks)
    monkeypatch.setattr(wiring, "_challenge_generator", lambda: TemplateChallengeGenerator())
    monkeypatch.setattr(wiring, "_reminder_repository", lambda: reminders)
    monkeypatch.setattr(wiring, "_notification_sender", lambda: sender)
    monkeypatch.setattr(wiring, "_weather_service", lambda: weather)
    settings.REMINDERS_KEY, settings.TELEGRAM_BOT_TOKEN, settings.TELEGRAM_BOT_USERNAME = KEY, "123:TOKEN", "Bot"
    return {"walks": walks, "reminders": reminders, "sender": sender, "weather": weather}


def test_the_context_endpoint_tells_the_weather_and_the_conditions(adapters):
    body = signed_in().get("/api/context?latitude=40.42&longitude=-3.7").json()

    assert (body["sky"], body["temperature_c"], body["suggested_weather"]) == ("rain", 17.0, "rainy")
    assert body["conditions"]["rain"] is True and "minutes_of_light" in body and body["sunset"].startswith("2026-10-09T19:42")


def test_the_context_endpoint_refuses_places_that_do_not_exist(adapters):
    assert signed_in().get("/api/context?latitude=140&longitude=-3.7").status_code == 422


def test_when_the_weather_service_is_down_the_context_says_unavailable(adapters):
    adapters["weather"].fail = True

    assert signed_in().get("/api/context?latitude=40.42&longitude=-3.7").status_code == 503


def test_a_walk_started_with_a_place_in_the_rain_keeps_its_conditions(adapters):
    body = {"user_id": "user-1", "mood": "calm", "minutes": 15, "weather": "rainy", "latitude": 40.42, "longitude": -3.7}

    response = signed_in().post("/api/walks", data=json.dumps(body), content_type="application/json")

    assert response.status_code == 201
    saved = adapters["walks"].find_or_fail_by_id(UUID(response.json()["id"]))
    assert "rain" in saved.conditions.split(",")  # (it may also be dark: the test clock is the real one)


def test_a_walk_without_a_place_still_works(adapters):
    body = {"user_id": "user-1", "mood": "calm", "minutes": 15}

    response = signed_in().post("/api/walks", data=json.dumps(body), content_type="application/json")

    assert response.status_code == 201 and adapters["weather"].asked == []


def _webhook(update):
    return signed_in().post("/api/telegram/webhook", data=json.dumps(update), content_type="application/json", HTTP_X_TELEGRAM_BOT_API_SECRET_TOKEN=SECRET)


def test_pressing_in_one_hour_in_telegram_snoozes_the_reminder(adapters):
    adapters["reminders"].save(a_reminder(telegram_chat_id="555"))

    response = _webhook({"update_id": 1, "callback_query": {"id": "cb-9", "data": "snooze", "message": {"chat": {"id": 555}}}})

    assert response.status_code == 204
    assert adapters["sender"].answers[0][0] == "cb-9" and adapters["reminders"].find_by_user_id("user-1").snoozed_until is not None


def test_the_reminder_settings_carry_the_place_without_sending_it_back(adapters):
    body = {"enabled": True, "weekday_time": "18:00", "weekend_time": "11:00", "timezone": "Europe/Madrid", "latitude": 40.4168, "longitude": -3.7038}

    saved = signed_in().put("/api/users/user-1/reminders", data=json.dumps(body), content_type="application/json").json()

    assert saved["has_place"] is True and "latitude" not in saved
    cleared = signed_in().put("/api/users/user-1/reminders", data=json.dumps({**body, "latitude": None, "longitude": None, "clear_place": True}), content_type="application/json").json()
    assert cleared["has_place"] is False
