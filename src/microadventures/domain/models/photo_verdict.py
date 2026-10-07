from dataclasses import dataclass


@dataclass(frozen=True)
class PhotoVerdict:
    accepted: bool
    reason: str = ""
