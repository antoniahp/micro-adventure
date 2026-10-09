from dataclasses import dataclass


@dataclass(frozen=True)
class FindYearlySummaryQuery:
    user_id: str
    year: int | None = None  # None is the current one
    timezone: str = "UTC"
