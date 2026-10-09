import hmac
import secrets
from datetime import datetime, timezone

from django.conf import settings
from ninja import Router, Status
from ninja.errors import HttpError

from api import wiring
from api.key_guard import check_key, webhook_secret
from api.telegram.telegram_serializer import TelegramLinkOut, TelegramUpdate
from microadventures.application.commands.create_telegram_link.create_telegram_link_command import CreateTelegramLinkCommand
from microadventures.application.commands.handle_telegram_callback.handle_telegram_callback_command import HandleTelegramCallbackCommand
from microadventures.application.commands.handle_telegram_message.handle_telegram_message_command import HandleTelegramMessageCommand
from microadventures.application.commands.register_bot_webhook.register_bot_webhook_command import RegisterBotWebhookCommand
from microadventures.application.commands.unlink_telegram.unlink_telegram_command import UnlinkTelegramCommand
from microadventures.domain.exceptions.notification_unavailable_exception import NotificationUnavailableException

router = Router()  # mounted at /telegram: what Telegram and the deploy call
user_router = Router()  # mounted at /users: what the web app calls


@router.post("/webhook", response={204: None})
def webhook(request, update: TelegramUpdate):
    """Telegram calls this each time someone writes to the bot."""
    if not settings.REMINDERS_KEY:
        raise HttpError(503, "REMINDERS_KEY is not set")
    sent = request.headers.get("X-Telegram-Bot-Api-Secret-Token", "")
    if not hmac.compare_digest(sent.encode(), webhook_secret().encode()):
        raise HttpError(403, "Wrong secret")
    message = update.message or {}
    chat_id, text = (message.get("chat") or {}).get("id"), message.get("text")
    if chat_id is not None and text:
        wiring.handle_telegram_message_handler().handle(HandleTelegramMessageCommand(chat_id=str(chat_id), text=text))
    callback = update.callback_query or {}
    callback_chat = ((callback.get("message") or {}).get("chat") or {}).get("id")
    if callback.get("id") and callback_chat is not None:
        wiring.handle_telegram_callback_handler().handle(
            HandleTelegramCallbackCommand(
                chat_id=str(callback_chat), callback_id=str(callback["id"]), data=str(callback.get("data", "")), now=datetime.now(timezone.utc)
            )
        )
    return Status(204, None)  # always 204: Telegram must not retry a message we did not understand


@router.post("/setup", response={204: None})
def setup(request, key: str):
    """Run once after deploying: tells Telegram to send what people write to this server."""
    check_key(key)
    wiring.register_bot_webhook_handler().handle(
        RegisterBotWebhookCommand(url=f"{settings.APP_URL}/api/telegram/webhook", secret=webhook_secret())
    )
    return Status(204, None)


@user_router.post("/{user_id}/telegram/link", response=TelegramLinkOut)
def link_telegram(request, user_id: str):
    """Gives the link that opens the bot with a one-time code. The bot connects the chat when it gets the code."""
    if not (settings.TELEGRAM_BOT_TOKEN and settings.TELEGRAM_BOT_USERNAME):
        raise NotificationUnavailableException()
    code = secrets.token_urlsafe(16)
    wiring.create_telegram_link_handler().handle(CreateTelegramLinkCommand(user_id=user_id, link_code=code))
    return {"url": f"https://t.me/{settings.TELEGRAM_BOT_USERNAME}?start={code}"}


@user_router.delete("/{user_id}/telegram", response={204: None})
def unlink_telegram(request, user_id: str):
    wiring.unlink_telegram_handler().handle(UnlinkTelegramCommand(user_id=user_id))
    return Status(204, None)
