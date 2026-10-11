from datetime import datetime, timezone

from microadventures.application.commands.accept_legal.accept_legal_command import AcceptLegalCommand
from microadventures.application.commands.accept_legal.accept_legal_command_handler import AcceptLegalCommandHandler
from microadventures.domain.models.legal import CURRENT_LEGAL_VERSION
from tests.fakes import InMemoryAccountRepository


def test_the_server_records_its_own_current_version_and_the_moment():
    accounts = InMemoryAccountRepository()
    accounts.claim("user-1")
    now = datetime(2026, 10, 11, 18, 30, tzinfo=timezone.utc)

    AcceptLegalCommandHandler(accounts).handle(AcceptLegalCommand(user_id="user-1", now=now))

    account = accounts.find_by_user_id("user-1")
    assert (account.legal_version, account.legal_accepted_at) == (CURRENT_LEGAL_VERSION, now)
