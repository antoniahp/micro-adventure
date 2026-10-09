from dataclasses import dataclass
from uuid import UUID

from microadventures.domain.models.language import Language


@dataclass(frozen=True)
class SwapChallengeCommand:
    walk_id: UUID
    challenge_id: UUID
    language: Language | None = None  # the language on screen now; the walk's own language if missing
