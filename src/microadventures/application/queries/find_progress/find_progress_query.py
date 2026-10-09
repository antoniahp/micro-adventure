from dataclasses import dataclass


@dataclass(frozen=True)
class FindProgressQuery:
    user_id: str
    timezone: str = "UTC"  # the days of a streak are the person's days
