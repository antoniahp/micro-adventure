class NotificationFailedException(Exception):
    def __init__(self, reason: str):
        super().__init__(f"The notification could not be sent: {reason}")
