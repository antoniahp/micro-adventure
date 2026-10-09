from datetime import datetime, timedelta, timezone
from uuid import uuid4

from microadventures.domain.models.challenge import Challenge
from microadventures.domain.models.challenge_category import ChallengeCategory
from microadventures.domain.models.mood import Mood
from microadventures.domain.models.reminder_settings import ReminderSettings
from microadventures.domain.models.walk import Walk
from microadventures.domain.models.weather import Sky, Weather


def a_challenge(**overrides) -> Challenge:
    values = {"id": uuid4(), "category": ChallengeCategory.NATURE, "text": "Encuentra el árbol más viejo."}
    return Challenge(**{**values, **overrides})


def a_walk(**overrides) -> Walk:
    values = {
        "id": uuid4(),
        "user_id": "user-1",
        "mood": Mood.CALM,
        "minutes": 30,
        "weather": "clear",
        "challenges": [a_challenge(), a_challenge(category=ChallengeCategory.SOUND)],
    }
    return Walk(**{**values, **overrides})


def a_reminder(**overrides) -> ReminderSettings:
    """Reminders on, Telegram connected, 18:00 on weekdays and 11:00 on weekends in Madrid."""
    values = {"user_id": "user-1", "enabled": True, "telegram_chat_id": "555", "timezone": "Europe/Madrid"}
    return ReminderSettings(**{**values, **overrides})


def a_weather(**overrides) -> Weather:
    """Madrid, a calm October day: 17 degrees, clear, the sun sets at 19:42 local time."""
    madrid = timezone(timedelta(hours=2))
    values = {
        "temperature_c": 17.0,
        "sky": Sky.CLEAR,
        "rain_mm": 0.0,
        "wind_kmh": 10.0,
        "sunrise": datetime(2026, 10, 9, 7, 50, tzinfo=madrid),
        "sunset": datetime(2026, 10, 9, 19, 42, tzinfo=madrid),
    }
    return Weather(**{**values, **overrides})
