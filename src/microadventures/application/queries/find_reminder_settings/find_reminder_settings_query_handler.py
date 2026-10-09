from microadventures.application.queries.find_reminder_settings.find_reminder_settings_query import FindReminderSettingsQuery
from microadventures.domain.models.reminder_settings import ReminderSettings
from microadventures.domain.services.reminder_service import ReminderService


class FindReminderSettingsQueryHandler:
    def __init__(self, reminder_service: ReminderService):
        self.reminder_service = reminder_service

    def handle(self, query: FindReminderSettingsQuery) -> ReminderSettings:
        """Someone who never set anything up gets the defaults, switched off."""
        return self.reminder_service.find_by_user_id(query.user_id) or ReminderSettings(user_id=query.user_id)
