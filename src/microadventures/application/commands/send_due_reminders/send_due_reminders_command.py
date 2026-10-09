from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class SendDueRemindersCommand:
    now: datetime  # with time zone; an outside clock calls this every few minutes
