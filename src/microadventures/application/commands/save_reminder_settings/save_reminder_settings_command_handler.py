import logging

from microadventures.application.commands.save_reminder_settings.save_reminder_settings_command import SaveReminderSettingsCommand
from microadventures.application.reminder_texts import text
from microadventures.domain.exceptions.notification_failed_exception import NotificationFailedException
from microadventures.domain.exceptions.notification_unavailable_exception import NotificationUnavailableException
from microadventures.domain.models.reminder_settings import ReminderSettings
from microadventures.domain.services.notification_sender import NotificationSender
from microadventures.domain.services.reminder_service import ReminderService

logger = logging.getLogger(__name__)


class SaveReminderSettingsCommandHandler:
    """Keeps the times, the time zone and the on/off switch. The Telegram connection is not touched.

    When the schedule changes and Telegram is connected, the bot confirms it, so the person knows it worked.
    """

    def __init__(self, reminder_service: ReminderService, notification_sender: NotificationSender | None = None):
        self.reminder_service = reminder_service
        self.notification_sender = notification_sender

    def handle(self, command: SaveReminderSettingsCommand) -> None:
        settings = self.reminder_service.find_by_user_id(command.user_id) or ReminderSettings(user_id=command.user_id)
        before = self._schedule(settings)
        settings.change(command.enabled, command.weekday_time, command.weekend_time, command.timezone, command.language)
        if command.clear_place:
            settings.clear_place()
        elif command.latitude is not None and command.longitude is not None:
            settings.set_place(command.latitude, command.longitude)
        self.reminder_service.save(settings)
        if self._schedule(settings) != before:
            self._confirm(settings)

    @staticmethod
    def _schedule(settings: ReminderSettings) -> tuple:
        return settings.enabled, settings.weekday_time, settings.weekend_time, settings.timezone

    def _confirm(self, settings: ReminderSettings) -> None:
        if self.notification_sender is None or not settings.is_linked:
            return
        key = "schedule_saved" if settings.enabled else "schedule_paused"
        message = text(settings.language, key, weekday=settings.weekday_time, weekend=settings.weekend_time)
        try:
            self.notification_sender.send(settings.telegram_chat_id, message)
        except (NotificationFailedException, NotificationUnavailableException) as error:
            logger.warning("Confirmation for %s not sent: %s", settings.user_id, error)  # the schedule is saved anyway
