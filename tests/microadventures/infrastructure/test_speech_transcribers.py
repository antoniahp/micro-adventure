import pytest
import requests

from microadventures.domain.exceptions.speech_transcription_failed_exception import SpeechTranscriptionFailedException
from microadventures.domain.exceptions.speech_transcription_unavailable_exception import SpeechTranscriptionUnavailableException
from microadventures.infrastructure.api.elevenlabs_speech_transcriber import ElevenLabsSpeechTranscriber
from microadventures.infrastructure.unavailable_speech_transcriber import UnavailableSpeechTranscriber


class FakeHttp:
    def __init__(self, body=None, error=None, delete_error=None):
        self.body = body
        self.error = error
        self.delete_error = delete_error
        self.requests = []
        self.deleted = []

    def delete(self, url, headers, timeout):
        self.deleted.append((url, headers))
        if self.delete_error:
            raise self.delete_error
        return self

    def post(self, url, headers, data, files, timeout):
        self.requests.append((url, headers, data, files))
        if self.error:
            raise self.error
        return self

    def raise_for_status(self):
        pass

    def json(self):
        return self.body


def test_elevenlabs_sends_the_audio_and_returns_the_text():
    http = FakeHttp({"text": " Un perro olisqueando una farola. "})

    text = ElevenLabsSpeechTranscriber("key", model="scribe_v2", http=http).transcribe(b"audio", "audio/webm")

    url, headers, data, files = http.requests[0]
    assert text == "Un perro olisqueando una farola."
    assert url == "https://api.elevenlabs.io/v1/speech-to-text"
    assert headers == {"xi-api-key": "key"}
    assert data == {"model_id": "scribe_v2"}
    assert files["file"] == ("voice-note", b"audio", "audio/webm")


def test_elevenlabs_deletes_the_transcript_from_its_history_once_the_text_is_back():
    http = FakeHttp({"text": "Un gorrión.", "transcription_id": "tr-1"})

    ElevenLabsSpeechTranscriber("key", http=http).transcribe(b"audio", "audio/webm")

    assert http.deleted == [("https://api.elevenlabs.io/v1/speech-to-text/transcripts/tr-1", {"xi-api-key": "key"})]


def test_a_failed_deletion_does_not_lose_the_text():
    http = FakeHttp({"text": "Un gorrión.", "transcription_id": "tr-1"}, delete_error=requests.ConnectionError("down"))

    assert ElevenLabsSpeechTranscriber("key", http=http).transcribe(b"audio", "audio/webm") == "Un gorrión."


def test_without_a_transcription_id_nothing_is_deleted():
    http = FakeHttp({"text": "Un gorrión."})

    ElevenLabsSpeechTranscriber("key", http=http).transcribe(b"audio", "audio/webm")

    assert http.deleted == []


def test_elevenlabs_fails_when_the_service_is_down():
    http = FakeHttp(error=requests.ConnectionError("down"))

    with pytest.raises(SpeechTranscriptionFailedException):
        ElevenLabsSpeechTranscriber("key", http=http).transcribe(b"audio", "audio/webm")


def test_elevenlabs_fails_when_no_speech_is_detected():
    with pytest.raises(SpeechTranscriptionFailedException):
        ElevenLabsSpeechTranscriber("key", http=FakeHttp({"text": "  "})).transcribe(b"audio", "audio/webm")


def test_unavailable_transcriber_says_so():
    with pytest.raises(SpeechTranscriptionUnavailableException):
        UnavailableSpeechTranscriber().transcribe(b"audio", "audio/webm")
