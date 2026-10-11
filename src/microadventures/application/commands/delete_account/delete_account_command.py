from dataclasses import dataclass


@dataclass(frozen=True)
class DeleteAccountCommand:
    user_id: str
