from microadventures.domain.models.reminder_settings import ReminderSettings
from microadventures.domain.services.reminder_service import ReminderService


class DbReminderRepository(ReminderService):
    def save(self, settings: ReminderSettings) -> None:
        settings.save()

    def find_by_user_id(self, user_id: str) -> ReminderSettings | None:
        return ReminderSettings.objects.filter(user_id=user_id).first()

    def find_by_link_code(self, code: str) -> ReminderSettings | None:
        return ReminderSettings.objects.filter(link_code=code).first() if code else None

    def find_by_telegram_chat_id(self, chat_id: str) -> ReminderSettings | None:
        return ReminderSettings.objects.filter(telegram_chat_id=chat_id).first() if chat_id else None

    def find_active(self) -> list[ReminderSettings]:
        return [s for s in ReminderSettings.objects.filter(enabled=True) if s.is_linked]
