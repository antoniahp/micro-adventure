class SpeechTranscriptionUnavailableException(Exception):
    def __init__(self):
        super().__init__("Voice transcription is not configured")
