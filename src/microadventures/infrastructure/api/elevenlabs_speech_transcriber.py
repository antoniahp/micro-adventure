import logging

import requests

from microadventures.domain.exceptions.speech_transcription_failed_exception import SpeechTranscriptionFailedException
from microadventures.domain.services.speech_transcriber import SpeechTranscriber

logger = logging.getLogger(__name__)


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
            body = response.json()
            text = body["text"].strip()
        except (requests.RequestException, KeyError, ValueError, AttributeError, TypeError) as error:
            raise SpeechTranscriptionFailedException(str(error)) from error

        self._forget(body.get("transcription_id"))
        if not text:
            raise SpeechTranscriptionFailedException("no speech was detected")
        return text

    def _forget(self, transcription_id: str | None) -> None:
        """ElevenLabs keeps every transcript (audio and text) in the account's history by default. The text is
        already back here, so it's deleted there right away: a voice note doesn't stay on a third party's servers."""
        if not transcription_id:
            return
        try:
            self.http.delete(
                f"{self.URL}/transcripts/{transcription_id}", headers={"xi-api-key": self.api_key}, timeout=10
            ).raise_for_status()
        except requests.RequestException as error:
            logger.warning("🎙️ The transcript could not be deleted at ElevenLabs: %s", type(error).__name__)
