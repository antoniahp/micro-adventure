from dataclasses import dataclass


@dataclass(frozen=True)
class FindProgressQuery:
    user_id: str
