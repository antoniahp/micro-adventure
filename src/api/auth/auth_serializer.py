from ninja import Schema
from pydantic import Field


class StartSessionIn(Schema):
    # An id the browser already used before sessions existed. Without it, a new one is created.
    user_id: str | None = Field(None, pattern=r"^[A-Za-z0-9-]{8,64}$")


class RefreshIn(Schema):
    refresh: str = Field(max_length=2000)


class SessionOut(Schema):
    user_id: str
    access: str
    refresh: str
