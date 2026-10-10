from datetime import datetime
from uuid import UUID

from ninja import Field, Schema

from microadventures.domain.models.language import Language
from microadventures.domain.models.mood import Mood
from microadventures.domain.models.walk import MAX_DIARY_LENGTH

MAX_STORY_LENGTH = 2000
MAX_PHOTO_BYTES = 5 * 1024 * 1024  # 5 MB: the client already shrinks photos well under this


class StartWalkIn(Schema):
    user_id: str
    mood: Mood
    minutes: int = Field(30, ge=5, le=240)
    weather: str = Field("unknown", max_length=50)
    challenges_count: int | None = Field(None, ge=1, le=10)  # None: the usual number for that much time
    note: str = Field("", max_length=500)
    language: Language = Language.ES
    latitude: float | None = Field(None, ge=-90, le=90)  # where the person is, if they allow it
    longitude: float | None = Field(None, ge=-180, le=180)


class FinishWalkIn(Schema):
    walked_minutes: int | None = Field(None, ge=1, le=720)
    distance_km: float | None = Field(None, ge=0, le=200)
    diary: str = Field("", max_length=MAX_DIARY_LENGTH)


class WalkCreatedOut(Schema):
    id: UUID


class ChallengeOut(Schema):
    id: UUID
    category: str
    text: str
    status: str
    accepts_photo: bool
    story: str
    source: str  # "template" or the name of the model that wrote the challenge


class WalkOut(Schema):
    id: UUID
    user_id: str
    mood: str
    minutes: int
    weather: str
    note: str
    language: str
    swaps_used: int
    walked_minutes: int | None
    distance_km: float | None
    diary: str
    finished_at: datetime | None
    created_at: datetime
    challenges: list[ChallengeOut]

    @staticmethod
    def resolve_diary(walk) -> str:
        return walk.diary or ""  # walks saved before this field existed have none
