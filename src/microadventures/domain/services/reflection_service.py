from abc import ABC, abstractmethod
from datetime import date

from microadventures.domain.models.weekly_reflection import WeeklyReflection


class ReflectionService(ABC):
    @abstractmethod
    def save(self, reflection: WeeklyReflection) -> None:
        raise NotImplementedError

    @abstractmethod
    def find_by_week(self, user_id: str, week_start: date) -> WeeklyReflection | None:
        raise NotImplementedError

    @abstractmethod
    def find_by_user_id(self, user_id: str) -> list[WeeklyReflection]:
        raise NotImplementedError
