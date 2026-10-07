class PhotoRejectedException(Exception):
    def __init__(self, reason: str):
        super().__init__(f"The photo does not match the challenge: {reason}")
