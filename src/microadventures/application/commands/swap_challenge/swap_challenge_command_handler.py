from microadventures.domain.models.challenge_brief import ChallengeBrief
from microadventures.domain.services.challenge_generator import ChallengeGenerator
from microadventures.domain.services.walk_service import WalkService

from microadventures.application.commands.swap_challenge.swap_challenge_command import SwapChallengeCommand


class SwapChallengeCommandHandler:
    def __init__(self, walk_service: WalkService, challenge_generator: ChallengeGenerator):
        self.walk_service = walk_service
        self.challenge_generator = challenge_generator

    def handle(self, command: SwapChallengeCommand) -> None:
        walk = self.walk_service.find_or_fail_by_id(command.walk_id)
        # Fail before asking the generator, so a refused swap costs no model call.
        walk.ensure_can_swap(command.challenge_id)
        current = walk.find_challenge(command.challenge_id)

        brief = ChallengeBrief(
            mood=walk.mood,
            minutes=walk.minutes,
            weather=walk.weather,
            count=1,
            category=current.category,
            note=walk.note,
            language=command.language or walk.language,
        )
        replacement = self.challenge_generator.generate(brief)[0]

        walk.swap_challenge(current.id, replacement)
        self.walk_service.save(walk)
