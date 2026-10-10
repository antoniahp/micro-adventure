from dataclasses import dataclass


@dataclass(frozen=True)
class ClaimAccountCommand:
    user_id: str
