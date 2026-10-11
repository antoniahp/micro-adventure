from django.utils import timezone

from microadventures.application.commands.accept_legal.accept_legal_command import AcceptLegalCommand
from microadventures.domain.models.legal import CURRENT_LEGAL_VERSION
from microadventures.domain.services.account_service import AccountService


class AcceptLegalCommandHandler:
    """Keeps the proof that this person saw the privacy policy and accepted the terms: which version, and when
    (GDPR art. 5.2, accountability). The server records its own current version, never one the browser claims."""

    def __init__(self, account_service: AccountService):
        self.account_service = account_service

    def handle(self, command: AcceptLegalCommand) -> None:
        self.account_service.accept_legal(command.user_id, CURRENT_LEGAL_VERSION, command.now or timezone.now())
