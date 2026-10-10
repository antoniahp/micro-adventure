from datetime import datetime, timezone

from django.conf import settings
from ninja import Router

from api import wiring
from api.auth.session import ensure_own_user
from api.key_guard import check_key
from api.reminders.reminders_serializer import ReminderSettingsIn, ReminderSettingsOut, RunOut
from microadventures.application.commands.save_reminder_settings.save_reminder_settings_command import SaveReminderSettingsCommand
from microadventures.application.queries.find_reminder_settings.find_reminder_settings_query import FindReminderSettingsQuery
from microadventures.application.commands.send_due_reminders.send_due_reminders_command import SendDueRemindersCommand

router = Router()  # mounted at /users
clock_router = Router()  # mounted at /reminders


def _out(reminder) -> dict:
    return {
        "enabled": reminder.enabled,
        "weekday_time": reminder.weekday_time,
        "weekend_time": reminder.weekend_time,
        "timezone": reminder.timezone,
        "language": reminder.language,
        "telegram_connected": reminder.is_linked,
        "has_place": reminder.has_place,
        "telegram_available": bool(settings.TELEGRAM_BOT_TOKEN and settings.TELEGRAM_BOT_USERNAME),
    }


@router.get("/{user_id}/reminders", response=ReminderSettingsOut)
def get_reminders(request, user_id: str):
    ensure_own_user(request, user_id)
    return _out(wiring.find_reminder_settings_handler().handle(FindReminderSettingsQuery(user_id=user_id)))


@router.put("/{user_id}/reminders", response=ReminderSettingsOut)
def save_reminders(request, user_id: str, payload: ReminderSettingsIn):
    ensure_own_user(request, user_id)
    wiring.save_reminder_settings_handler().handle(
        SaveReminderSettingsCommand(
            user_id=user_id,
            enabled=payload.enabled,
            weekday_time=payload.weekday_time,
            weekend_time=payload.weekend_time,
            timezone=payload.timezone,
            language=payload.language,
            latitude=payload.latitude,
            longitude=payload.longitude,
            clear_place=payload.clear_place,
        )
    )
    return _out(wiring.find_reminder_settings_handler().handle(FindReminderSettingsQuery(user_id=user_id)))


@clock_router.post("/run", response=RunOut)
def run(request, key: str):
    """The outside clock calls this every few minutes. It sends the reminders whose time has come."""
    check_key(key)
    sent = wiring.send_due_reminders_handler().handle(SendDueRemindersCommand(now=datetime.now(timezone.utc)))
    return {"sent": sent}
