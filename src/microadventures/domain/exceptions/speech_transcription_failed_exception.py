class SpeechTranscriptionFailedException(Exception):
    def __init__(self, reason: str):
        super().__init__(f"The voice note could not be transcribed: {reason}")
