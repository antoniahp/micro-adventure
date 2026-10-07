from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class FindWalkQuery:
    walk_id: UUID
