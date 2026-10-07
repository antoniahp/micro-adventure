from microadventures.application.queries.transcribe_audio.transcribe_audio_query import TranscribeAudioQuery
from microadventures.domain.services.speech_transcriber import SpeechTranscriber


class TranscribeAudioQueryHandler:
    """Turns a voice note into text. It changes nothing: the person reviews the text before sending it."""

    def __init__(self, speech_transcriber: SpeechTranscriber):
        self.speech_transcriber = speech_transcriber

    def handle(self, query: TranscribeAudioQuery) -> str:
        return self.speech_transcriber.transcribe(query.audio, query.content_type)
