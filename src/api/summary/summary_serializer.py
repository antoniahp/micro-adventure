from datetime import date

from ninja import Field, Schema


class DayOut(Schema):
    day: date
    walks: int
    challenges: int


class WeeklySummaryOut(Schema):
    week_start: date
    week_end: date
    walks_count: int
    days_walked: int
    challenges_completed: int
    perfect_walks: int
    minutes: int
    km: float
    stories: int
    days: list[DayOut]
    moods: dict[str, int]
    categories: dict[str, int]
    previous_walks: int
    previous_challenges: int
    previous_minutes: int
    previous_km: float
    feeling: int | None
    feeling_note: str


class WeeklyReflectionIn(Schema):
    week: date  # any day of the week
    feeling: int = Field(..., ge=1, le=5)
    note: str = Field("", max_length=500)


class MonthOut(Schema):
    month: int
    walks: int
    challenges: int
    minutes: int
    km: float
    feeling: float | None


class YearlySummaryOut(Schema):
    year: int
    years: list[int]
    walks_count: int
    days_walked: int
    challenges_completed: int
    perfect_walks: int
    minutes: int
    km: float
    stories: int
    longest_streak: int
    best_month: int | None
    months: list[MonthOut]
    moods: dict[str, int]
    categories: dict[str, int]
    weekdays: list[int]
