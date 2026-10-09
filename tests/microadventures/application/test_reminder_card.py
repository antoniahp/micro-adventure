from datetime import datetime, timedelta, timezone

import pytest

from tests.fakes import FakeWeatherService, InMemoryReminderRepository, SpyNotificationSender
from tests.microadventures.object_mothers import a_reminder, a_weather
from microadventures.application.commands.handle_telegram_callback.handle_telegram_callback_command import HandleTelegramCallbackCommand
from microadventures.application.commands.handle_telegram_callback.handle_telegram_callback_command_handler import HandleTelegramCallbackCommandHandler
from microadventures.application.commands.save_reminder_settings.save_reminder_settings_command import SaveReminderSettingsCommand
from microadventures.application.commands.save_reminder_settings.save_reminder_settings_command_handler import SaveReminderSettingsCommandHandler
from microadventures.application.commands.send_due_reminders.send_due_reminders_command import SendDueRemindersCommand
from microadventures.application.commands.send_due_reminders.send_due_reminders_command_handler import SendDueRemindersCommandHandler
from microadventures.application.reminder_card_builder import build_reminder_card
from microadventures.application.reminder_texts import format_light
from microadventures.domain.exceptions.invalid_reminder_settings_exception import InvalidReminderSettingsException
from microadventures.domain.models.language import Language
from microadventures.domain.models.weather import Sky

APP_URL = "https://micro-adventure.onrender.com"
FRIDAY_18_00 = datetime(2026, 10, 9, 16, 0, tzinfo=timezone.utc)  # in Madrid, 1 h 42 min before the sun sets
FRIDAY_21_00 = datetime(2026, 10, 9, 19, 0, tzinfo=timezone.utc)
SATURDAY_11_30 = datetime(2026, 10, 10, 9, 30, tzinfo=timezone.utc)


def _card(weather=None, now=FRIDAY_18_00, weekend=False, **settings):
    return build_reminder_card(a_reminder(**settings), weekend, weather, now, APP_URL)


# --- the card ---

def test_it_says_the_light_that_is_left_and_the_weather():
    card = _card(a_weather())

    assert "Tu jornada ha terminado" in card.caption
    assert "<b>1 h 42 min</b> de luz" in card.caption and "17 °C, despejado" in card.caption


def test_after_dark_it_suggests_lit_streets_instead_of_counting_light():
    card = _card(a_weather(), now=FRIDAY_21_00)

    assert "de noche" in card.caption and "calles con luz" in card.caption and "de luz ·" not in card.caption


def test_with_rain_it_says_there_are_covered_challenges():
    assert "bajo cubierto" in _card(a_weather(sky=Sky.RAIN)).caption


def test_without_the_weather_it_still_invites():
    card = _card(None)

    assert "Un paseo corto con retos" in card.caption and "°C" not in card.caption


def test_the_weekend_has_its_own_picture_and_words():
    card = _card(None, now=SATURDAY_11_30, weekend=True)

    assert "Buena hora para salir" in card.caption and card.photo_url == f"{APP_URL}/reminder-weekend.png"
    assert _card(None).photo_url == f"{APP_URL}/reminder-weekday.png"


def test_the_card_is_in_english_when_the_person_uses_english():
    card = _card(a_weather(), language=Language.EN)

    assert "You're done for today" in card.caption and "of daylight left" in card.caption and card.snooze_label == "⏰ In 1 hour"


def test_without_the_address_of_the_app_there_is_no_picture_and_no_open_button():
    card = build_reminder_card(a_reminder(), False, None, FRIDAY_18_00, "")

    assert card.photo_url == "" and card.open_url == ""


def test_the_light_is_written_for_people():
    assert (format_light(102, "es"), format_light(35, "es"), format_light(120, "es")) == ("1 h 42 min", "35 min", "2 h")


# --- sending it ---

def _send(reminders, weather_service, now=FRIDAY_18_00):
    sender = SpyNotificationSender()
    handler = SendDueRemindersCommandHandler(reminders, sender, APP_URL, weather_service)
    return handler.handle(SendDueRemindersCommand(now=now)), sender


def _reminders(**settings):
    repository = InMemoryReminderRepository()
    repository.save(a_reminder(**settings))
    return repository


def test_the_reminder_carries_the_weather_where_the_person_is():
    weather = FakeWeatherService(a_weather())

    sent, sender = _send(_reminders(latitude=40.42, longitude=-3.7), weather)

    assert sent == 1 and weather.asked == [(40.42, -3.7)] and "1 h 42 min" in sender.cards[0][1].caption


def test_without_a_shared_place_the_weather_is_not_asked():
    weather = FakeWeatherService(a_weather())

    _, sender = _send(_reminders(), weather)

    assert weather.asked == [] and "°C" not in sender.cards[0][1].caption


def test_if_the_weather_fails_the_reminder_still_goes_out():
    sent, sender = _send(_reminders(latitude=40.42, longitude=-3.7), FakeWeatherService(fail=True))

    assert sent == 1 and "°C" not in sender.cards[0][1].caption


# --- the buttons ---

def _press(reminders, data, chat="555", now=FRIDAY_18_00):
    sender = SpyNotificationSender()
    HandleTelegramCallbackCommandHandler(reminders, sender).handle(HandleTelegramCallbackCommand(chat, "cb-1", data, now))
    return sender


def test_in_one_hour_brings_the_reminder_back_even_after_it_was_sent():
    reminders = _reminders()
    _send(reminders, None)  # sent at 18:00 and marked as sent for the day

    sender = _press(reminders, "snooze")

    assert sender.answers == [("cb-1", "Vale, te aviso en 1 hora ⏰")]
    assert _send(reminders, None, FRIDAY_18_00 + timedelta(minutes=30))[0] == 0  # not yet
    assert _send(reminders, None, FRIDAY_18_00 + timedelta(minutes=61))[0] == 1  # now


def test_the_snoozed_reminder_is_sent_once_and_then_the_snooze_is_over():
    reminders = _reminders()
    _press(reminders, "snooze")
    later = FRIDAY_18_00 + timedelta(hours=1, minutes=5)

    first, _ = _send(reminders, None, later)
    second, _ = _send(reminders, None, later + timedelta(minutes=10))

    assert (first, second) == (1, 0) and reminders.find_by_user_id("user-1").snoozed_until is None


def test_not_today_lets_the_day_go_but_tomorrow_it_comes_back():
    reminders = _reminders()

    sender = _press(reminders, "skip")

    assert sender.answers == [("cb-1", "Hecho, hoy no te molesto más 😴")]
    assert _send(reminders, None)[0] == 0
    assert _send(reminders, None, SATURDAY_11_30)[0] == 1  # tomorrow it is back


def test_a_snooze_that_nobody_uses_expires_after_the_late_window():
    reminders = _reminders()
    _press(reminders, "snooze")

    assert _send(reminders, None, FRIDAY_18_00 + timedelta(hours=1) + timedelta(hours=3, minutes=1))[0] == 0


def test_a_button_pressed_by_someone_unknown_or_with_other_data_is_just_answered():
    reminders = _reminders()

    assert _press(reminders, "snooze", chat="999").answers == [("cb-1", "")]
    assert _press(reminders, "dance").answers == [("cb-1", "")]
    assert reminders.find_by_user_id("user-1").snoozed_until is None


# --- the place ---

def test_the_place_is_kept_to_about_a_kilometre():
    reminders = _reminders()

    SaveReminderSettingsCommandHandler(reminders).handle(
        SaveReminderSettingsCommand("user-1", True, "18:00", "11:00", "Europe/Madrid", Language.ES, latitude=40.416775, longitude=-3.70379)
    )

    saved = reminders.find_by_user_id("user-1")
    assert (saved.latitude, saved.longitude) == (40.42, -3.7) and saved.has_place


def test_saving_without_a_place_keeps_the_one_there_was_and_it_can_be_cleared():
    reminders = _reminders(latitude=40.42, longitude=-3.7)
    command = SaveReminderSettingsCommand("user-1", True, "18:00", "11:00", "Europe/Madrid", Language.ES)

    SaveReminderSettingsCommandHandler(reminders).handle(command)
    assert reminders.find_by_user_id("user-1").has_place

    SaveReminderSettingsCommandHandler(reminders).handle(
        SaveReminderSettingsCommand("user-1", True, "18:00", "11:00", "Europe/Madrid", Language.ES, clear_place=True)
    )
    assert not reminders.find_by_user_id("user-1").has_place


def test_a_place_that_does_not_exist_is_refused():
    with pytest.raises(InvalidReminderSettingsException):
        a_reminder().set_place(123, 10)


def test_changing_the_schedule_cancels_a_pending_snooze():
    reminder = a_reminder()
    reminder.snooze(FRIDAY_18_00)

    reminder.change(True, "19:00", "11:00", "Europe/Madrid", Language.ES)

    assert reminder.snoozed_until is None
