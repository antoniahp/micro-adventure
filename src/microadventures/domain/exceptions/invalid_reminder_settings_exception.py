class InvalidReminderSettingsException(Exception):
    def __init__(self, reason: str):
        super().__init__(f"Invalid reminder settings: {reason}")
