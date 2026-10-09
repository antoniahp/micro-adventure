import logging

from microadventures.application.commands.send_due_reminders.send_due_reminders_command import SendDueRemindersCommand
from microadventures.application.reminder_texts import text
from microadventures.domain.exceptions.notification_failed_exception import NotificationFailedException
from microadventures.domain.models.reminder_settings import ReminderSettings
from microadventures.domain.services.notification_sender import NotificationSender
from microadventures.domain.services.reminder_service import ReminderService
from microadventures.domain.services.walk_criteria import WalkCriteria
from microadventures.domain.services.walk_service import WalkService

logger = logging.getLogger(__name__)


class SendDueRemindersCommandHandler:
    """Sends the reminders whose time has come, at most one per person and day.

    Whoever already started a walk today gets none: the reminder would only be noise.
    """

    def __init__(self, reminder_service: ReminderService, walk_service: WalkService, notification_sender: NotificationSender, app_url: str):
        self.reminder_service = reminder_service
        self.walk_service = walk_service
        self.notification_sender = notification_sender
        self.app_url = app_url

    def handle(self, command: SendDueRemindersCommand) -> int:
        sent = 0
        for settings in self.reminder_service.find_active():
            if not settings.is_due(command.now):
                continue
            if self._walked_today(settings, command):
                settings.mark_sent(command.now)  # nothing to remind of, and nothing to try again today
                self.reminder_service.save(settings)
                continue
            try:
                self.notification_sender.send(settings.telegram_chat_id, self._message(settings, command))
            except NotificationFailedException as error:
                logger.warning("Reminder for %s not sent: %s", settings.user_id, error)  # tried again at the next call
                continue
            settings.mark_sent(command.now)
            self.reminder_service.save(settings)
            sent += 1
        return sent

    def _walked_today(self, settings: ReminderSettings, command: SendDueRemindersCommand) -> bool:
        today = settings.local_day(command.now)
        walks = self.walk_service.find_by_criteria(WalkCriteria(user_id=settings.user_id))
        return any(settings.local_day(walk.created_at) == today for walk in walks)

    def _message(self, settings: ReminderSettings, command: SendDueRemindersCommand) -> str:
        weekend = settings.local_day(command.now).weekday() >= 5
        return text(settings.language, "weekend" if weekend else "weekday", url=self.app_url)
