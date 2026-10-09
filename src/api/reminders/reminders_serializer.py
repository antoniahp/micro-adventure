from ninja import Field, Schema

from microadventures.domain.models.language import Language


class ReminderSettingsIn(Schema):
    enabled: bool
    weekday_time: str = Field(..., max_length=5)
    weekend_time: str = Field(..., max_length=5)
    timezone: str = Field(..., max_length=64)
    language: Language = Language.ES
    latitude: float | None = Field(None, ge=-90, le=90)
    longitude: float | None = Field(None, ge=-180, le=180)
    clear_place: bool = False


class ReminderSettingsOut(Schema):
    enabled: bool
    weekday_time: str
    weekend_time: str
    timezone: str
    language: str
    telegram_connected: bool
    has_place: bool  # the weather of the reminder needs a place
    telegram_available: bool  # false when the server has no bot configured


class RunOut(Schema):
    sent: int
