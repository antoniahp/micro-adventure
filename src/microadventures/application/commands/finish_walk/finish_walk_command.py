from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class FinishWalkCommand:
    walk_id: UUID
    walked_minutes: int | None = None
    distance_km: float | None = None
    diary: str = ""
