from dataclasses import dataclass


@dataclass(frozen=True)
class SetNicknameCommand:
    user_id: str
    nickname: str | None
