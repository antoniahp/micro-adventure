from dataclasses import dataclass


@dataclass(frozen=True)
class FindAccountQuery:
    user_id: str
