from microadventures.application.commands.unlink_telegram.unlink_telegram_command import UnlinkTelegramCommand
from microadventures.domain.services.reminder_service import ReminderService


class UnlinkTelegramCommandHandler:
    def __init__(self, reminder_service: ReminderService):
        self.reminder_service = reminder_service

    def handle(self, command: UnlinkTelegramCommand) -> None:
        settings = self.reminder_service.find_by_user_id(command.user_id)
        if settings is None:
            return
        settings.unlink_telegram()
        self.reminder_service.save(settings)
