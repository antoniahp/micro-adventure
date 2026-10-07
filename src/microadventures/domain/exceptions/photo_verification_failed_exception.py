class PhotoVerificationFailedException(Exception):
    def __init__(self, reason: str):
        super().__init__(f"Could not verify the photo: {reason}")
