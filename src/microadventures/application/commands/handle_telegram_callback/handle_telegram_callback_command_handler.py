from microadventures.application.commands.handle_telegram_callback.handle_telegram_callback_command import HandleTelegramCallbackCommand
from microadventures.application.reminder_texts import card_text
from microadventures.domain.services.notification_sender import NotificationSender
from microadventures.domain.services.reminder_service import ReminderService


class HandleTelegramCallbackCommandHandler:
    """What the buttons of a reminder do: 'in one hour' brings it back later, 'not today' lets the day go."""

    def __init__(self, reminder_service: ReminderService, notification_sender: NotificationSender):
        self.reminder_service = reminder_service
        self.notification_sender = notification_sender

    def handle(self, command: HandleTelegramCallbackCommand) -> None:
        settings = self.reminder_service.find_by_telegram_chat_id(command.chat_id)
        if settings is None or command.data not in ("snooze", "skip"):
            self.notification_sender.answer(command.callback_id, "")  # Telegram keeps the button spinning until it is answered
            return
        if command.data == "snooze":
            settings.snooze(command.now)
        else:
            settings.skip_today(command.now)
        self.reminder_service.save(settings)
        self.notification_sender.answer(command.callback_id, card_text(settings.language, "snoozed" if command.data == "snooze" else "skipped"))
