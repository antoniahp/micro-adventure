from datetime import date

from microadventures.domain.models.weekly_reflection import WeeklyReflection
from microadventures.domain.services.reflection_service import ReflectionService


class DbReflectionRepository(ReflectionService):
    def save(self, reflection: WeeklyReflection) -> None:
        reflection.save()

    def find_by_week(self, user_id: str, week_start: date) -> WeeklyReflection | None:
        return WeeklyReflection.objects.filter(user_id=user_id, week_start=week_start).first()

    def find_by_user_id(self, user_id: str) -> list[WeeklyReflection]:
        return list(WeeklyReflection.objects.filter(user_id=user_id))
