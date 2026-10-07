from dataclasses import dataclass
from typing import Optional
from uuid import UUID


@dataclass(frozen=True)
class WalkCriteria:
    id: Optional[UUID] = None
    user_id: Optional[str] = None
