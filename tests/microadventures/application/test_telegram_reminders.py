from datetime import datetime, timezone
from uuid import uuid4

from tests.fakes import InMemoryReminderRepository, InMemoryWalkRepository, SpyNotificationSender
from tests.microadventures.object_mothers import a_reminder, a_walk
from microadventures.application.commands.create_telegram_link.create_telegram_link_command import CreateTelegramLinkCommand
from microadventures.application.commands.create_telegram_link.create_telegram_link_command_handler import CreateTelegramLinkCommandHandler
from microadventures.application.commands.handle_telegram_message.handle_telegram_message_command import HandleTelegramMessageCommand
from microadventures.application.commands.handle_telegram_message.handle_telegram_message_command_handler import HandleTelegramMessageCommandHandler
from microadventures.application.commands.register_bot_webhook.register_bot_webhook_command import RegisterBotWebhookCommand
from microadventures.application.commands.register_bot_webhook.register_bot_webhook_command_handler import RegisterBotWebhookCommandHandler
from microadventures.application.commands.save_reminder_settings.save_reminder_settings_command import SaveReminderSettingsCommand
from microadventures.application.commands.save_reminder_settings.save_reminder_settings_command_handler import SaveReminderSettingsCommandHandler
from microadventures.application.commands.send_due_reminders.send_due_reminders_command import SendDueRemindersCommand
from microadventures.application.commands.send_due_reminders.send_due_reminders_command_handler import SendDueRemindersCommandHandler
from microadventures.application.commands.unlink_telegram.unlink_telegram_command import UnlinkTelegramCommand
from microadventures.application.commands.unlink_telegram.unlink_telegram_command_handler import UnlinkTelegramCommandHandler
from microadventures.application.queries.find_reminder_settings.find_reminder_settings_query import FindReminderSettingsQuery
from microadventures.application.queries.find_reminder_settings.find_reminder_settings_query_handler import FindReminderSettingsQueryHandler
from microadventures.domain.models.language import Language

FRIDAY_18_30_MADRID = datetime(2026, 10, 9, 16, 30, tzinfo=timezone.utc)
SATURDAY_11_30_MADRID = datetime(2026, 10, 10, 9, 30, tzinfo=timezone.utc)
APP_URL = "https://micro-adventure.onrender.com"


def _repository_with(*reminders):
    repository = InMemoryReminderRepository()
    for reminder in reminders:
        repository.save(reminder)
    return repository


def _send_due(reminders, now, sender=None, walks=None):
    sender = sender or SpyNotificationSender()
    handler = SendDueRemindersCommandHandler(reminders, walks or InMemoryWalkRepository(), sender, APP_URL)
    return handler.handle(SendDueRemindersCommand(now=now)), sender


# --- settings ---

def test_someone_without_settings_gets_the_defaults_switched_off():
    found = FindReminderSettingsQueryHandler(InMemoryReminderRepository()).handle(FindReminderSettingsQuery(user_id="new"))

    assert (found.enabled, found.weekday_time, found.weekend_time, found.is_linked) == (False, "18:00", "11:00", False)


def test_it_saves_the_times_without_touching_the_telegram_connection():
    repository = _repository_with(a_reminder())

    SaveReminderSettingsCommandHandler(repository).handle(
        SaveReminderSettingsCommand("user-1", True, "19:30", "10:00", "Europe/Madrid", Language.EN)
    )

    saved = repository.find_by_user_id("user-1")
    assert (saved.weekday_time, saved.weekend_time, saved.language, saved.telegram_chat_id) == ("19:30", "10:00", "en", "555")


def test_it_creates_the_settings_the_first_time_they_are_saved():
    repository = InMemoryReminderRepository()

    SaveReminderSettingsCommandHandler(repository).handle(
        SaveReminderSettingsCommand("user-9", False, "18:00", "11:00", "Europe/Madrid", Language.ES)
    )

    assert repository.find_by_user_id("user-9") is not None


def test_the_bot_confirms_a_new_schedule_when_telegram_is_connected():
    sender = SpyNotificationSender()
    repository = _repository_with(a_reminder())

    SaveReminderSettingsCommandHandler(repository, sender).handle(
        SaveReminderSettingsCommand("user-1", True, "23:40", "10:00", "Europe/Madrid", Language.ES)
    )

    assert len(sender.sent) == 1
    assert sender.sent[0][0] == "555" and "23:40" in sender.sent[0][1]


def test_the_bot_says_nothing_when_nothing_changed():
    sender = SpyNotificationSender()
    repository = _repository_with(a_reminder())
    command = SaveReminderSettingsCommand("user-1", True, "19:30", "10:00", "Europe/Madrid", Language.ES)
    SaveReminderSettingsCommandHandler(repository).handle(command)

    SaveReminderSettingsCommandHandler(repository, sender).handle(command)

    assert sender.sent == []


def test_the_bot_says_it_is_off_when_the_reminders_are_switched_off():
    sender = SpyNotificationSender()
    repository = _repository_with(a_reminder())

    SaveReminderSettingsCommandHandler(repository, sender).handle(
        SaveReminderSettingsCommand("user-1", False, "19:30", "10:00", "Europe/Madrid", Language.EN)
    )

    assert len(sender.sent) == 1 and "off" in sender.sent[0][1]


def test_it_saves_the_schedule_even_when_the_confirmation_cannot_be_sent():
    repository = _repository_with(a_reminder())

    SaveReminderSettingsCommandHandler(repository, SpyNotificationSender(fail=True)).handle(
        SaveReminderSettingsCommand("user-1", True, "23:40", "10:00", "Europe/Madrid", Language.ES)
    )

    assert repository.find_by_user_id("user-1").weekday_time == "23:40"


def test_nobody_is_written_to_before_connecting_telegram():
    sender = SpyNotificationSender()
    repository = InMemoryReminderRepository()

    SaveReminderSettingsCommandHandler(repository, sender).handle(
        SaveReminderSettingsCommand("user-9", True, "20:00", "11:00", "Europe/Madrid", Language.ES)
    )

    assert sender.sent == []


# --- connecting Telegram ---

def test_the_link_code_is_kept_until_the_chat_uses_it():
    repository = InMemoryReminderRepository()

    CreateTelegramLinkCommandHandler(repository).handle(CreateTelegramLinkCommand("user-1", "code-1"))

    assert repository.find_by_link_code("code-1").user_id == "user-1"


def test_writing_start_with_the_code_connects_the_chat_and_confirms_it():
    repository = _repository_with(a_reminder(enabled=False, telegram_chat_id="", link_code="code-1", language=Language.ES))
    sender = SpyNotificationSender()

    HandleTelegramMessageCommandHandler(repository, sender).handle(HandleTelegramMessageCommand("999", "/start code-1"))

    saved = repository.find_by_user_id("user-1")
    assert (saved.telegram_chat_id, saved.enabled, saved.link_code) == ("999", True, "")
    assert sender.sent[0][0] == "999" and "18:00" in sender.sent[0][1] and "Conectado" in sender.sent[0][1]


def test_the_confirmation_is_in_the_language_of_the_person():
    repository = _repository_with(a_reminder(enabled=False, telegram_chat_id="", link_code="c", language=Language.EN))
    sender = SpyNotificationSender()

    HandleTelegramMessageCommandHandler(repository, sender).handle(HandleTelegramMessageCommand("999", "/start c"))

    assert "Connected" in sender.sent[0][1]


def test_a_code_works_only_once():
    repository = _repository_with(a_reminder(enabled=False, telegram_chat_id="", link_code="code-1"))
    sender = SpyNotificationSender()
    handler = HandleTelegramMessageCommandHandler(repository, sender)

    handler.handle(HandleTelegramMessageCommand("999", "/start code-1"))
    handler.handle(HandleTelegramMessageCommand("111", "/start code-1"))

    assert repository.find_by_user_id("user-1").telegram_chat_id == "999"
    assert "ya no vale" in sender.sent[1][1]


def test_an_unknown_code_changes_nothing_and_explains_how_to_connect():
    repository = _repository_with(a_reminder(telegram_chat_id="555"))
    sender = SpyNotificationSender()

    HandleTelegramMessageCommandHandler(repository, sender).handle(HandleTelegramMessageCommand("999", "/start nope"))

    assert repository.find_by_user_id("user-1").telegram_chat_id == "555"
    assert "ya no vale" in sender.sent[0][1] and "no longer valid" in sender.sent[0][1]


def test_start_with_the_bot_name_is_the_same_command():
    repository = _repository_with(a_reminder(enabled=False, telegram_chat_id="", link_code="c"))

    HandleTelegramMessageCommandHandler(repository, SpyNotificationSender()).handle(
        HandleTelegramMessageCommand("999", "/start@MicroAdventuresBot c")
    )

    assert repository.find_by_user_id("user-1").is_linked


def test_stop_switches_the_reminders_off_and_forgets_the_chat():
    repository = _repository_with(a_reminder(telegram_chat_id="555"))
    sender = SpyNotificationSender()

    HandleTelegramMessageCommandHandler(repository, sender).handle(HandleTelegramMessageCommand("555", "/stop"))

    saved = repository.find_by_user_id("user-1")
    assert (saved.enabled, saved.is_linked) == (False, False)
    assert sender.sent and sender.sent[0][0] == "555"


def test_anything_else_says_how_to_connect():
    sender = SpyNotificationSender()

    HandleTelegramMessageCommandHandler(InMemoryReminderRepository(), sender).handle(HandleTelegramMessageCommand("999", "hola"))

    assert "Conectar Telegram" in sender.sent[0][1]


def test_the_person_can_disconnect_from_the_app():
    repository = _repository_with(a_reminder())

    UnlinkTelegramCommandHandler(repository).handle(UnlinkTelegramCommand("user-1"))
    UnlinkTelegramCommandHandler(repository).handle(UnlinkTelegramCommand("nobody"))  # nothing to do, no error

    assert not repository.find_by_user_id("user-1").is_linked


def test_it_registers_the_webhook():
    sender = SpyNotificationSender()

    RegisterBotWebhookCommandHandler(sender).handle(RegisterBotWebhookCommand("https://x/api/telegram/webhook", "secret"))

    assert sender.registered == [("https://x/api/telegram/webhook", "secret")]


# --- sending the reminders ---

def test_it_sends_a_reminder_when_the_time_has_come_and_only_once():
    repository = _repository_with(a_reminder())

    first, sender = _send_due(repository, FRIDAY_18_30_MADRID)
    second, _ = _send_due(repository, FRIDAY_18_30_MADRID, sender)

    assert (first, second) == (1, 0)
    card = sender.cards[0][1]
    assert sender.cards[0][0] == "555" and card.open_url == APP_URL and "Tu jornada ha terminado" in card.caption


def test_it_sends_nothing_before_the_time():
    sent, sender = _send_due(_repository_with(a_reminder()), datetime(2026, 10, 9, 14, 0, tzinfo=timezone.utc))

    assert (sent, sender.cards) == (0, [])


def test_the_weekend_message_is_different():
    _, sender = _send_due(_repository_with(a_reminder()), SATURDAY_11_30_MADRID)

    assert "Buena hora para salir" in sender.cards[0][1].caption and sender.cards[0][1].photo_url.endswith("reminder-weekend.png")


def test_the_reminder_is_in_the_language_of_the_person():
    _, sender = _send_due(_repository_with(a_reminder(language=Language.EN)), FRIDAY_18_30_MADRID)

    assert "done for today" in sender.cards[0][1].caption and sender.cards[0][1].snooze_label == "⏰ In 1 hour"


def test_whoever_already_walked_today_gets_no_reminder():
    walks = InMemoryWalkRepository()
    walks.save(a_walk(user_id="user-1", created_at=datetime(2026, 10, 9, 12, 0, tzinfo=timezone.utc)))
    repository = _repository_with(a_reminder())

    sent, sender = _send_due(repository, FRIDAY_18_30_MADRID, walks=walks)

    assert (sent, sender.cards) == (0, [])
    assert repository.find_by_user_id("user-1").last_sent_on is not None  # and it does not try again today


def test_a_walk_from_another_day_does_not_stop_the_reminder():
    walks = InMemoryWalkRepository()
    walks.save(a_walk(user_id="user-1", created_at=datetime(2026, 10, 8, 12, 0, tzinfo=timezone.utc)))

    sent, _ = _send_due(_repository_with(a_reminder()), FRIDAY_18_30_MADRID, walks=walks)

    assert sent == 1


def test_a_failed_send_is_tried_again_at_the_next_call():
    repository = _repository_with(a_reminder())

    sent, _ = _send_due(repository, FRIDAY_18_30_MADRID, SpyNotificationSender(fail=True))
    retried, _ = _send_due(repository, FRIDAY_18_30_MADRID)

    assert (sent, retried) == (0, 1)


def test_it_reminds_everyone_whose_time_has_come():
    repository = _repository_with(a_reminder(user_id="a", telegram_chat_id="1"), a_reminder(user_id="b", telegram_chat_id="2"))

    sent, sender = _send_due(repository, FRIDAY_18_30_MADRID)

    assert sent == 2 and {chat for chat, _ in sender.cards} == {"1", "2"}
