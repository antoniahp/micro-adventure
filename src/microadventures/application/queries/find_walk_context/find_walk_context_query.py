from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class FindWalkContextQuery:
    latitude: float
    longitude: float
    now: datetime  # with time zone
