from microadventures.application.commands.handle_telegram_message.handle_telegram_message_command import HandleTelegramMessageCommand
from microadventures.application.reminder_texts import both_languages, text
from microadventures.domain.services.notification_sender import NotificationSender
from microadventures.domain.services.reminder_service import ReminderService


class HandleTelegramMessageCommandHandler:
    """What the bot does with what people write to it: connect a chat, stop the reminders, or say how to connect."""

    def __init__(self, reminder_service: ReminderService, notification_sender: NotificationSender):
        self.reminder_service = reminder_service
        self.notification_sender = notification_sender

    def handle(self, command: HandleTelegramMessageCommand) -> None:
        words = command.text.strip().split()
        word = words[0].split("@")[0].lower() if words else ""  # "/start@MyBot" is the same as "/start"
        if word == "/start" and len(words) > 1:
            self._link(command.chat_id, words[1])
        elif word == "/stop":
            self._stop(command.chat_id)
        else:
            self.notification_sender.send(command.chat_id, both_languages("help"))

    def _link(self, chat_id: str, code: str) -> None:
        settings = self.reminder_service.find_by_link_code(code)
        if settings is None:
            self.notification_sender.send(chat_id, both_languages("unknown_code"))
            return
        settings.link_telegram(chat_id)
        self.reminder_service.save(settings)
        self.notification_sender.send(
            chat_id, text(settings.language, "linked", weekday=settings.weekday_time, weekend=settings.weekend_time)
        )

    def _stop(self, chat_id: str) -> None:
        settings = self.reminder_service.find_by_telegram_chat_id(chat_id)
        if settings is not None:
            settings.unlink_telegram()
            self.reminder_service.save(settings)
        self.notification_sender.send(chat_id, text(settings.language if settings else "es", "stopped"))
