from microadventures.application.commands.create_telegram_link.create_telegram_link_command import CreateTelegramLinkCommand
from microadventures.domain.models.reminder_settings import ReminderSettings
from microadventures.domain.services.reminder_service import ReminderService


class CreateTelegramLinkCommandHandler:
    def __init__(self, reminder_service: ReminderService):
        self.reminder_service = reminder_service

    def handle(self, command: CreateTelegramLinkCommand) -> None:
        settings = self.reminder_service.find_by_user_id(command.user_id) or ReminderSettings(user_id=command.user_id)
        settings.start_linking(command.link_code)
        self.reminder_service.save(settings)
