from microadventures.application.commands.warm_up_generator.warm_up_generator_command import WarmUpGeneratorCommand
from microadventures.domain.services.challenge_generator import ChallengeGenerator


class WarmUpGeneratorCommandHandler:
    def __init__(self, challenge_generator: ChallengeGenerator):
        self.challenge_generator = challenge_generator

    def handle(self, command: WarmUpGeneratorCommand) -> None:
        self.challenge_generator.warm_up()
