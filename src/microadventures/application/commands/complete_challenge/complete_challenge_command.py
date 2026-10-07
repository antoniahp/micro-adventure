from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class CompleteChallengeCommand:
    walk_id: UUID
    challenge_id: UUID
    photo: bytes | None = None
    story: str = ""
