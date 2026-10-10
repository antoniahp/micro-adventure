from microadventures.application.commands.link_google_account.link_google_account_command import LinkGoogleAccountCommand
from microadventures.domain.services.account_service import AccountService
from microadventures.domain.services.google_identity_verifier import GoogleIdentityVerifier


class LinkGoogleAccountCommandHandler:
    """Links this browser's account to a Google identity, or, if that identity already belongs to a
    different account (a reinstall, a new phone), hands back that account's id instead of creating a
    second one — so the person gets their walks and badges back rather than a second, empty account.
    """

    def __init__(self, account_service: AccountService, verifier: GoogleIdentityVerifier):
        self.account_service = account_service
        self.verifier = verifier

    def handle(self, command: LinkGoogleAccountCommand) -> str:
        sub, email = self.verifier.verify(command.id_token)
        existing = self.account_service.find_by_google_sub(sub)
        if existing is not None and existing.user_id != command.user_id:
            return existing.user_id
        self.account_service.link_google(command.user_id, sub, email)
        return command.user_id
