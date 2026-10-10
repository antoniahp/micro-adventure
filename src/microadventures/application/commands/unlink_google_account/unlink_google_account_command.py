from dataclasses import dataclass


@dataclass(frozen=True)
class UnlinkGoogleAccountCommand:
    user_id: str
