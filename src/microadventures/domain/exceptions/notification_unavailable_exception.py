class NotificationUnavailableException(Exception):
    def __init__(self):
        super().__init__("Notifications are not configured: the Telegram bot token is missing")
