from dataclasses import dataclass

from microadventures.domain.models.language import Language


@dataclass(frozen=True)
class SaveReminderSettingsCommand:
    user_id: str
    enabled: bool
    weekday_time: str
    weekend_time: str
    timezone: str
    language: Language
    latitude: float | None = None  # shared only if the person wants the weather in the reminder
    longitude: float | None = None
    clear_place: bool = False
