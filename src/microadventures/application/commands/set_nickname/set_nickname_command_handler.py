from microadventures.application.commands.set_nickname.set_nickname_command import SetNicknameCommand
from microadventures.domain.services.account_service import AccountService


class SetNicknameCommandHandler:
    def __init__(self, account_service: AccountService):
        self.account_service = account_service

    def handle(self, command: SetNicknameCommand) -> None:
        nickname = command.nickname.strip() if command.nickname else None
        self.account_service.set_nickname(command.user_id, nickname or None)
