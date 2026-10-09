from datetime import date, datetime, timezone

import pytest

from tests.microadventures.object_mothers import a_reminder
from microadventures.domain.exceptions.invalid_reminder_settings_exception import InvalidReminderSettingsException
from microadventures.domain.models.language import Language

# Friday 9 October 2026 and Saturday 10 October 2026. Madrid is two hours ahead of UTC (summer time).
FRIDAY = (2026, 10, 9)
SATURDAY = (2026, 10, 10)


def utc(day, hour, minute=0):
    return datetime(*day, hour, minute, tzinfo=timezone.utc)


def test_a_weekday_reminder_is_due_from_the_chosen_time():
    reminder = a_reminder()  # 18:00 in Madrid = 16:00 UTC

    assert not reminder.is_due(utc(FRIDAY, 15, 59))
    assert reminder.is_due(utc(FRIDAY, 16, 0))
    assert reminder.is_due(utc(FRIDAY, 18, 59))


def test_it_is_no_longer_due_three_hours_later():
    assert not a_reminder().is_due(utc(FRIDAY, 19, 0))


def test_the_weekend_has_its_own_time():
    reminder = a_reminder()  # 11:00 in Madrid = 09:00 UTC

    assert not reminder.is_due(utc(SATURDAY, 8, 59))
    assert reminder.is_due(utc(SATURDAY, 9, 0))
    assert not reminder.is_due(utc(SATURDAY, 16, 30))  # the weekday time does not apply on Saturday


def test_it_uses_the_time_zone_of_the_person():
    reminder = a_reminder(timezone="America/Mexico_City")  # UTC-6 in October: 18:00 there is 00:00 UTC next day

    assert not reminder.is_due(utc(FRIDAY, 16, 30))
    assert reminder.is_due(utc((2026, 10, 10), 0, 30))  # still Friday evening in Mexico


def test_it_is_due_once_a_day():
    reminder = a_reminder()
    now = utc(FRIDAY, 16, 30)

    reminder.mark_sent(now)

    assert not reminder.is_due(utc(FRIDAY, 17, 0))
    assert reminder.is_due(utc((2026, 10, 12), 16, 30))  # Monday


def test_a_new_time_can_fire_again_the_same_day():
    reminder = a_reminder()  # 18:30 in Madrid on weekdays
    reminder.mark_sent(utc(FRIDAY, 16, 30))

    reminder.change(True, "19:00", reminder.weekend_time, reminder.timezone, reminder.language)

    assert reminder.is_due(utc(FRIDAY, 17, 5))  # 19:05 in Madrid


def test_saving_the_same_settings_does_not_repeat_the_reminder():
    reminder = a_reminder()
    reminder.mark_sent(utc(FRIDAY, 16, 30))

    reminder.change(reminder.enabled, reminder.weekday_time, reminder.weekend_time, reminder.timezone, reminder.language)

    assert not reminder.is_due(utc(FRIDAY, 17, 0))


def test_the_day_is_the_local_one():
    reminder = a_reminder(timezone="Asia/Tokyo")  # UTC+9: 23:30 UTC on Friday is already Saturday morning

    assert reminder.local_day(utc(FRIDAY, 23, 30)) == date(2026, 10, 10)


def test_it_is_never_due_when_switched_off_or_not_connected():
    assert not a_reminder(enabled=False).is_due(utc(FRIDAY, 16, 30))
    assert not a_reminder(telegram_chat_id="").is_due(utc(FRIDAY, 16, 30))


@pytest.mark.parametrize("bad_time", ["", "6pm", "25:00", "18:60", "18", "18:00:00"])
def test_it_refuses_times_that_are_not_a_time(bad_time):
    with pytest.raises(InvalidReminderSettingsException):
        a_reminder().change(True, bad_time, "11:00", "Europe/Madrid", Language.ES)


def test_it_refuses_an_unknown_time_zone():
    with pytest.raises(InvalidReminderSettingsException):
        a_reminder().change(True, "18:00", "11:00", "Mars/Olympus", Language.ES)


def test_linking_uses_the_code_once_and_switches_the_reminders_on():
    reminder = a_reminder(enabled=False, telegram_chat_id="")
    reminder.start_linking("abc")

    reminder.link_telegram("777")

    assert (reminder.telegram_chat_id, reminder.link_code, reminder.enabled) == ("777", "", True)


def test_unlinking_forgets_the_chat_and_switches_the_reminders_off():
    reminder = a_reminder()

    reminder.unlink_telegram()

    assert (reminder.telegram_chat_id, reminder.enabled, reminder.is_linked) == ("", False, False)
