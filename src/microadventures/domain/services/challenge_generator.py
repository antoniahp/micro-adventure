from abc import ABC, abstractmethod

from microadventures.domain.models.challenge import Challenge
from microadventures.domain.models.challenge_brief import ChallengeBrief


class ChallengeGenerator(ABC):
    @abstractmethod
    def generate(self, brief: ChallengeBrief) -> list[Challenge]:
        raise NotImplementedError

    def warm_up(self) -> None:
        """Gets the generator ready for the next call. Does nothing unless it has something to prepare."""
