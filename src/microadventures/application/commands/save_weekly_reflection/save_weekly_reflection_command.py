from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class SaveWeeklyReflectionCommand:
    user_id: str
    week: date  # any day of the week
    feeling: int  # 1 to 5
    note: str = ""
