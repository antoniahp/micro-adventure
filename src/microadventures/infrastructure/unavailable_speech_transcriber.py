from microadventures.domain.exceptions.speech_transcription_unavailable_exception import SpeechTranscriptionUnavailableException
from microadventures.domain.services.speech_transcriber import SpeechTranscriber


class UnavailableSpeechTranscriber(SpeechTranscriber):
    """Used when no transcription service is configured: the person can still write the story."""

    def transcribe(self, audio: bytes, content_type: str) -> str:
        raise SpeechTranscriptionUnavailableException()
