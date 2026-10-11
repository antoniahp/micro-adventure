from datetime import date

from microadventures.application.commands.delete_account.delete_account_command import DeleteAccountCommand
from microadventures.application.commands.delete_account.delete_account_command_handler import DeleteAccountCommandHandler
from microadventures.domain.models.reminder_settings import ReminderSettings
from microadventures.domain.models.walk import Walk
from microadventures.domain.models.weekly_reflection import WeeklyReflection
from microadventures.domain.services.walk_criteria import WalkCriteria
from tests.fakes import (
    InMemoryAccountRepository,
    InMemoryReflectionRepository,
    InMemoryReminderRepository,
    InMemoryWalkRepository,
)


def _everything_for(user_id, walks, reflections, reminders, accounts):
    walks.save(Walk(user_id=user_id, mood="calm", minutes=20, weather="sunny", diary="I saw a heron", challenges=[]))
    walks.save(Walk(user_id=user_id, mood="curious", minutes=10, weather="cloudy", challenges=[]))
    reflections.save(WeeklyReflection(user_id=user_id, week_start=date(2026, 10, 5), feeling=4, note="good week"))
    reminders.save(ReminderSettings(user_id=user_id, telegram_chat_id=f"chat-{user_id}"))
    accounts.claim(user_id)
    accounts.set_nickname(user_id, "Jose")
    accounts.link_google(user_id, f"google-{user_id}", "someone@example.com")


def test_deleting_an_account_removes_everything_of_that_person_and_nothing_of_anyone_else():
    walks, reflections = InMemoryWalkRepository(), InMemoryReflectionRepository()
    reminders, accounts = InMemoryReminderRepository(), InMemoryAccountRepository()
    _everything_for("user-1", walks, reflections, reminders, accounts)
    _everything_for("user-2", walks, reflections, reminders, accounts)

    DeleteAccountCommandHandler(walks, reflections, reminders, accounts).handle(DeleteAccountCommand(user_id="user-1"))

    assert walks.find_by_criteria(WalkCriteria(user_id="user-1")) == []
    assert reflections.find_by_user_id("user-1") == []
    assert reminders.find_by_user_id("user-1") is None
    assert reminders.find_by_telegram_chat_id("chat-user-1") is None
    assert accounts.find_by_user_id("user-1") is None
    assert accounts.find_by_google_sub("google-user-1") is None

    assert len(walks.find_by_criteria(WalkCriteria(user_id="user-2"))) == 2
    assert len(reflections.find_by_user_id("user-2")) == 1
    assert reminders.find_by_user_id("user-2") is not None
    assert accounts.find_by_user_id("user-2").nickname == "Jose"


def test_deleting_an_account_that_has_nothing_is_fine():
    handler = DeleteAccountCommandHandler(
        InMemoryWalkRepository(), InMemoryReflectionRepository(), InMemoryReminderRepository(), InMemoryAccountRepository()
    )

    handler.handle(DeleteAccountCommand(user_id="nobody"))  # no error: deleting twice is harmless
