from dataclasses import dataclass


@dataclass(frozen=True)
class FindReminderSettingsQuery:
    user_id: str
