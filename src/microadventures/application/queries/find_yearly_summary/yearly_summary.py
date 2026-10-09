from dataclasses import dataclass, field


@dataclass(frozen=True)
class MonthSummary:
    month: int  # 1 to 12
    walks: int
    challenges: int
    minutes: int
    km: float
    feeling: float | None  # average of the weeks that start in that month, if the person answered any


@dataclass(frozen=True)
class YearlySummary:
    year: int
    years: list[int]  # the years with walks, plus this one, so the person can move between them
    walks_count: int
    days_walked: int
    challenges_completed: int
    perfect_walks: int
    minutes: int
    km: float
    stories: int
    longest_streak: int
    best_month: int | None
    months: list[MonthSummary] = field(default_factory=list)
    moods: dict[str, int] = field(default_factory=dict)
    categories: dict[str, int] = field(default_factory=dict)
    weekdays: list[int] = field(default_factory=list)  # walks from Monday to Sunday
