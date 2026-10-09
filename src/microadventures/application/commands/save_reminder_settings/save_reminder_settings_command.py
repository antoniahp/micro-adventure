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
