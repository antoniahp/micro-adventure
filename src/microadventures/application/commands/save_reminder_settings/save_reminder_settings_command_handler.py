from microadventures.application.commands.save_reminder_settings.save_reminder_settings_command import SaveReminderSettingsCommand
from microadventures.domain.models.reminder_settings import ReminderSettings
from microadventures.domain.services.reminder_service import ReminderService


class SaveReminderSettingsCommandHandler:
    """Keeps the times, the time zone and the on/off switch. The Telegram connection is not touched."""

    def __init__(self, reminder_service: ReminderService):
        self.reminder_service = reminder_service

    def handle(self, command: SaveReminderSettingsCommand) -> None:
        settings = self.reminder_service.find_by_user_id(command.user_id) or ReminderSettings(user_id=command.user_id)
        settings.change(command.enabled, command.weekday_time, command.weekend_time, command.timezone, command.language)
        self.reminder_service.save(settings)
