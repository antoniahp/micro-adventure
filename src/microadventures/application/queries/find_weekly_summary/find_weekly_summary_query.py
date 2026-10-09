from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class FindWeeklySummaryQuery:
    user_id: str
    week: date | None = None  # any day of the week; None is the current one
    timezone: str = "UTC"
