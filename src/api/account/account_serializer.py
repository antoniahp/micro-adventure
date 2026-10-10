from ninja import Field, Schema


class NicknameIn(Schema):
    nickname: str | None = Field(None, max_length=50)


class GoogleLinkIn(Schema):
    id_token: str = Field(..., max_length=4096)


class AccountOut(Schema):
    nickname: str | None
    google_linked: bool


class GoogleLinkOut(AccountOut):
    # True when the credential belonged to an account other than this browser's: the session was switched
    # to that one (access/refresh are then set) instead of linking Google to this browser's own account.
    switched: bool
    user_id: str
    access: str | None
    refresh: str | None
