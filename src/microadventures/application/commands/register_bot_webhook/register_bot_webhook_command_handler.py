from microadventures.application.commands.register_bot_webhook.register_bot_webhook_command import RegisterBotWebhookCommand
from microadventures.domain.services.bot_webhook import BotWebhook


class RegisterBotWebhookCommandHandler:
    def __init__(self, bot_webhook: BotWebhook):
        self.bot_webhook = bot_webhook

    def handle(self, command: RegisterBotWebhookCommand) -> None:
        self.bot_webhook.register(command.url, command.secret)
