from microadventures.application.commands.finish_walk.finish_walk_command import FinishWalkCommand
from microadventures.domain.services.walk_service import WalkService


class FinishWalkCommandHandler:
    """Closes a walk with the real time, the distance and the story, all of them optional."""

    def __init__(self, walk_service: WalkService):
        self.walk_service = walk_service

    def handle(self, command: FinishWalkCommand) -> None:
        walk = self.walk_service.find_or_fail_by_id(command.walk_id)
        walk.finish(command.walked_minutes, command.distance_km, command.diary)
        self.walk_service.save(walk)
