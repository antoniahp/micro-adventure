from microadventures.domain.models.challenge_brief import ChallengeBrief
from microadventures.domain.services.challenge_generator import ChallengeGenerator
from microadventures.domain.services.walk_service import WalkService
from microadventures.domain.models.walk import Walk

from microadventures.application.commands.start_walk.start_walk_command import StartWalkCommand


class StartWalkCommandHandler:
    def __init__(self, walk_service: WalkService, challenge_generator: ChallengeGenerator):
        self.walk_service = walk_service
        self.challenge_generator = challenge_generator

    def handle(self, command: StartWalkCommand) -> None:
        brief = ChallengeBrief(
            mood=command.mood,
            minutes=command.minutes,
            weather=command.weather,
            count=command.challenges_count,
            note=command.note,
            language=command.language,
        )
        walk = Walk(
            id=command.walk_id,
            user_id=command.user_id,
            mood=command.mood,
            minutes=command.minutes,
            weather=command.weather,
            note=command.note,
            language=command.language,
            challenges=self.challenge_generator.generate(brief),
        )
        self.walk_service.save(walk)
