from abc import ABC, abstractmethod


class SpeechTranscriber(ABC):
    @abstractmethod
    def transcribe(self, audio: bytes, content_type: str) -> str:
        raise NotImplementedError
