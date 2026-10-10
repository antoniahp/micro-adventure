from dataclasses import dataclass


@dataclass(frozen=True)
class LinkGoogleAccountCommand:
    user_id: str
    id_token: str
