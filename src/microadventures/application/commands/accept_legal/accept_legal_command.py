from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class AcceptLegalCommand:
    user_id: str
    now: datetime | None = None  # tests pass a fixed time
