from microadventures.application.commands.claim_account.claim_account_command import ClaimAccountCommand
from microadventures.domain.exceptions.account_already_claimed_exception import AccountAlreadyClaimedException
from microadventures.domain.services.account_service import AccountService


class ClaimAccountCommandHandler:
    def __init__(self, account_service: AccountService):
        self.account_service = account_service

    def handle(self, command: ClaimAccountCommand) -> None:
        if not self.account_service.claim(command.user_id):
            raise AccountAlreadyClaimedException()
