import requests

from microadventures.domain.exceptions.speech_transcription_failed_exception import SpeechTranscriptionFailedException
from microadventures.domain.services.speech_transcriber import SpeechTranscriber


class ElevenLabsSpeechTranscriber(SpeechTranscriber):
    URL = "https://api.elevenlabs.io/v1/speech-to-text"

    def __init__(self, api_key: str, model: str = "scribe_v2", timeout_seconds: float = 60, http=requests):
        self.api_key = api_key
        self.model = model
        self.timeout_seconds = timeout_seconds
        self.http = http

    def transcribe(self, audio: bytes, content_type: str) -> str:
        try:
            response = self.http.post(
                self.URL,
                headers={"xi-api-key": self.api_key},
                data={"model_id": self.model},
                files={"file": ("voice-note", audio, content_type)},
                timeout=self.timeout_seconds,
            )
            response.raise_for_status()
            text = response.json()["text"].strip()
        except (requests.RequestException, KeyError, ValueError, AttributeError) as error:
            raise SpeechTranscriptionFailedException(str(error)) from error

        if not text:
            raise SpeechTranscriptionFailedException("no speech was detected")
        return text
