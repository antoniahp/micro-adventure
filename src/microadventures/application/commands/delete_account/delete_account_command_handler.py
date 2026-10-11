from microadventures.application.commands.delete_account.delete_account_command import DeleteAccountCommand
from microadventures.domain.services.account_service import AccountService
from microadventures.domain.services.reflection_service import ReflectionService
from microadventures.domain.services.reminder_service import ReminderService
from microadventures.domain.services.walk_service import WalkService


class DeleteAccountCommandHandler:
    """Everything kept about a person goes, for good: walks (with their challenges and stories), weekly
    reflections, reminders (with the Telegram chat id) and the account itself (nickname and Google link).
    The account goes last, so if anything fails halfway the person can simply try again."""

    def __init__(
        self,
        walk_service: WalkService,
        reflection_service: ReflectionService,
        reminder_service: ReminderService,
        account_service: AccountService,
    ):
        self.walk_service = walk_service
        self.reflection_service = reflection_service
        self.reminder_service = reminder_service
        self.account_service = account_service

    def handle(self, command: DeleteAccountCommand) -> None:
        self.walk_service.delete_by_user_id(command.user_id)
        self.reflection_service.delete_by_user_id(command.user_id)
        self.reminder_service.delete_by_user_id(command.user_id)
        self.account_service.delete_by_user_id(command.user_id)
