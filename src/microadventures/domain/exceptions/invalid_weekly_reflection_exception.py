class InvalidWeeklyReflectionException(Exception):
    def __init__(self, reason: str):
        super().__init__(f"Invalid weekly reflection: {reason}")
