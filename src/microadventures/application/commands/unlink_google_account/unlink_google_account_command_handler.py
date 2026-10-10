from microadventures.application.commands.unlink_google_account.unlink_google_account_command import (
    UnlinkGoogleAccountCommand,
)
from microadventures.domain.services.account_service import AccountService


class UnlinkGoogleAccountCommandHandler:
    def __init__(self, account_service: AccountService):
        self.account_service = account_service

    def handle(self, command: UnlinkGoogleAccountCommand) -> None:
        self.account_service.unlink_google(command.user_id)
