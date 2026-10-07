from datetime import datetime
from uuid import UUID

from ninja import Field, Schema

from microadventures.domain.models.mood import Mood


class StartWalkIn(Schema):
    user_id: str
    mood: Mood
    minutes: int = Field(30, ge=5, le=240)
    weather: str = "unknown"
    challenges_count: int = Field(3, ge=1, le=10)
    note: str = Field("", max_length=500)


class WalkCreatedOut(Schema):
    id: UUID


class ChallengeOut(Schema):
    id: UUID
    category: str
    text: str
    status: str
    accepts_photo: bool
    story: str


class WalkOut(Schema):
    id: UUID
    user_id: str
    mood: str
    minutes: int
    weather: str
    note: str
    swaps_used: int
    created_at: datetime
    challenges: list[ChallengeOut]


class ProgressOut(Schema):
    walks_count: int
    days_walked: int
    challenges_completed: int
    perfect_walks: int
    stickers: list[str]
