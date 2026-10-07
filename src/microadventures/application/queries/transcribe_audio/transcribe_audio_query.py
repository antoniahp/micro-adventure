from dataclasses import dataclass


@dataclass(frozen=True)
class TranscribeAudioQuery:
    audio: bytes
    content_type: str
