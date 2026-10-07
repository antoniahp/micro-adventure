from microadventures.application.queries.transcribe_audio.transcribe_audio_query import TranscribeAudioQuery
from microadventures.application.queries.transcribe_audio.transcribe_audio_query_handler import TranscribeAudioQueryHandler
from microadventures.domain.services.speech_transcriber import SpeechTranscriber


class StubSpeechTranscriber(SpeechTranscriber):
    def __init__(self, text: str):
        self.text = text
        self.received = []

    def transcribe(self, audio: bytes, content_type: str) -> str:
        self.received.append((audio, content_type))
        return self.text


def test_it_returns_the_text_of_the_voice_note():
    transcriber = StubSpeechTranscriber("He oído un mirlo cerca de la fuente.")

    text = TranscribeAudioQueryHandler(transcriber).handle(TranscribeAudioQuery(audio=b"audio", content_type="audio/webm"))

    assert text == "He oído un mirlo cerca de la fuente."
    assert transcriber.received == [(b"audio", "audio/webm")]
