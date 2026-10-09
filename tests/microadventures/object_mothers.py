from uuid import uuid4

from microadventures.domain.models.challenge import Challenge
from microadventures.domain.models.challenge_category import ChallengeCategory
from microadventures.domain.models.mood import Mood
from microadventures.domain.models.reminder_settings import ReminderSettings
from microadventures.domain.models.walk import Walk


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
