import logging

from microadventures.application.commands.send_due_reminders.send_due_reminders_command import SendDueRemindersCommand
from microadventures.application.reminder_card_builder import build_reminder_card
from microadventures.domain.exceptions.notification_failed_exception import NotificationFailedException
from microadventures.domain.exceptions.weather_unavailable_exception import WeatherUnavailableException
from microadventures.domain.models.weather import Weather
from microadventures.domain.models.reminder_settings import ReminderSettings
from microadventures.domain.services.notification_sender import NotificationSender
from microadventures.domain.services.reminder_service import ReminderService
from microadventures.domain.services.weather_service import WeatherService

logger = logging.getLogger(__name__)


class SendDueRemindersCommandHandler:
    """Sends the reminders whose time has come, at most one per person and day."""

    def __init__(self, reminder_service: ReminderService, notification_sender: NotificationSender, app_url: str, weather_service: WeatherService | None = None):
        self.reminder_service = reminder_service
        self.notification_sender = notification_sender
        self.app_url = app_url
        self.weather_service = weather_service

    def handle(self, command: SendDueRemindersCommand) -> int:
        sent = 0
        for settings in self.reminder_service.find_active():
            if not settings.is_due(command.now):
                continue
            try:
                self.notification_sender.send_card(settings.telegram_chat_id, self._card(settings, command))
            except NotificationFailedException as error:
                logger.warning("Reminder for %s not sent: %s", settings.user_id, error)  # tried again at the next call
                continue
            settings.mark_sent(command.now)
            self.reminder_service.save(settings)
            sent += 1
        return sent

    def _card(self, settings: ReminderSettings, command: SendDueRemindersCommand):
        weekend = settings.local_day(command.now).weekday() >= 5
        return build_reminder_card(settings, weekend, self._weather(settings), command.now, self.app_url)

    def _weather(self, settings: ReminderSettings) -> Weather | None:
        """The weather where the person said they are, if they did. Without it the reminder just invites."""
        if self.weather_service is None or not settings.has_place:
            return None
        try:
            return self.weather_service.at(settings.latitude, settings.longitude)
        except WeatherUnavailableException as error:
            logger.warning("Reminder for %s without weather: %s", settings.user_id, error)
            return None
