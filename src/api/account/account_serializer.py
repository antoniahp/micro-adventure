from ninja import Field, Schema


class NicknameIn(Schema):
    nickname: str | None = Field(None, max_length=50)


class GoogleLinkIn(Schema):
    id_token: str = Field(..., max_length=4096)


class AccountOut(Schema):
    nickname: str | None
    google_linked: bool
    legal_accepted: bool  # accepted the current version of the privacy policy and terms (domain/models/legal.py)
    support_code: str  # short code to quote when writing about one's data (domain/models/support_code.py)


class GoogleLinkOut(AccountOut):
    # True when the credential belonged to an account other than this browser's: the session was switched
    # to that one (access/refresh are then set) instead of linking Google to this browser's own account.
    switched: bool
    user_id: str
    access: str | None
    refresh: str | None
