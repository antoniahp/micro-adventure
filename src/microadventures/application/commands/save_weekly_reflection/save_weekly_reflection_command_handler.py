from microadventures.application.commands.save_weekly_reflection.save_weekly_reflection_command import SaveWeeklyReflectionCommand
from microadventures.domain.models.walk_history import monday_of
from microadventures.domain.models.weekly_reflection import WeeklyReflection
from microadventures.domain.services.reflection_service import ReflectionService


class SaveWeeklyReflectionCommandHandler:
    """Writing it again for the same week replaces what was said before."""

    def __init__(self, reflection_service: ReflectionService):
        self.reflection_service = reflection_service

    def handle(self, command: SaveWeeklyReflectionCommand) -> None:
        week_start = monday_of(command.week)
        reflection = self.reflection_service.find_by_week(command.user_id, week_start) or WeeklyReflection(
            user_id=command.user_id, week_start=week_start
        )
        reflection.change(command.feeling, command.note)
        self.reflection_service.save(reflection)
