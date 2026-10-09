from datetime import date, datetime, time, timedelta
from uuid import uuid4
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from django.db import models
from django.utils import timezone as django_timezone

from microadventures.domain.exceptions.invalid_reminder_settings_exception import InvalidReminderSettingsException
from microadventures.domain.models.language import Language

DEFAULT_WEEKDAY_TIME = "18:00"  # when the working day usually ends
DEFAULT_WEEKEND_TIME = "11:00"  # a good moment in the middle of the day
DEFAULT_TIMEZONE = "Europe/Madrid"
LATE_AFTER = timedelta(hours=3)  # a reminder this late is no longer useful, so it is skipped


def parse_time(text: str) -> time:
    """'18:30' -> time(18, 30). Anything else is refused."""
    try:
        hour, minute = text.split(":")
        return time(int(hour), int(minute))
    except (ValueError, AttributeError):
        raise InvalidReminderSettingsException(f"'{text}' is not a time like 18:30")


def parse_timezone(name: str) -> ZoneInfo:
    try:
        return ZoneInfo(name)
    except (ZoneInfoNotFoundError, ValueError, KeyError):
        raise InvalidReminderSettingsException(f"'{name}' is not a known time zone")


class ReminderSettings(models.Model):
    """When to remind a person to go out, and where (their Telegram chat). One per anonymous user."""

    id = models.UUIDField(primary_key=True, default=uuid4)
    user_id = models.CharField(max_length=100, unique=True)
    enabled = models.BooleanField(default=False)
    weekday_time = models.CharField(max_length=5, default=DEFAULT_WEEKDAY_TIME)
    weekend_time = models.CharField(max_length=5, default=DEFAULT_WEEKEND_TIME)
    timezone = models.CharField(max_length=64, default=DEFAULT_TIMEZONE)
    language = models.CharField(max_length=5, choices=Language.choices, default=Language.ES)
    telegram_chat_id = models.CharField(max_length=30, blank=True, default="")
    link_code = models.CharField(max_length=40, blank=True, default="", db_index=True)
    last_sent_on = models.DateField(null=True, blank=True)  # the local day of the last reminder
    updated_at = models.DateTimeField(default=django_timezone.now)

    def change(self, enabled: bool, weekday_time: str, weekend_time: str, timezone: str, language: Language) -> None:
        parse_time(weekday_time), parse_time(weekend_time), parse_timezone(timezone)  # raise when wrong
        schedule = (enabled, weekday_time, weekend_time, timezone)
        if schedule != (self.enabled, self.weekday_time, self.weekend_time, self.timezone):
            self.last_sent_on = None  # a new schedule may fire again today, even if one reminder already went out
        self.enabled = enabled
        self.weekday_time = weekday_time
        self.weekend_time = weekend_time
        self.timezone = timezone
        self.language = language
        self.updated_at = django_timezone.now()

    @property
    def is_linked(self) -> bool:
        return bool(self.telegram_chat_id)

    def start_linking(self, code: str) -> None:
        self.link_code = code

    def link_telegram(self, chat_id: str) -> None:
        self.telegram_chat_id = chat_id
        self.link_code = ""  # a code works once
        self.enabled = True

    def unlink_telegram(self) -> None:
        self.telegram_chat_id = ""
        self.link_code = ""
        self.enabled = False

    def local_day(self, now: datetime) -> date:
        return now.astimezone(parse_timezone(self.timezone)).date()

    def time_for(self, day: date) -> time:
        """Saturday and Sunday have their own time."""
        return parse_time(self.weekend_time if day.weekday() >= 5 else self.weekday_time)

    def is_due(self, now: datetime) -> bool:
        """True from the chosen time until three hours later, once per day."""
        if not (self.enabled and self.is_linked):
            return False
        zone = parse_timezone(self.timezone)
        local = now.astimezone(zone)
        if self.last_sent_on == local.date():
            return False
        start = datetime.combine(local.date(), self.time_for(local.date()), tzinfo=zone)
        return start <= local < start + LATE_AFTER

    def mark_sent(self, now: datetime) -> None:
        self.last_sent_on = self.local_day(now)

    def __str__(self):
        return f"{self.user_id} · {'on' if self.enabled else 'off'}"
