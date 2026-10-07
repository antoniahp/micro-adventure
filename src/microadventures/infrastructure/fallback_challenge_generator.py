import logging

from microadventures.domain.models.challenge import Challenge
from microadventures.domain.models.challenge_brief import ChallengeBrief
from microadventures.domain.services.challenge_generator import ChallengeGenerator

logger = logging.getLogger(__name__)


class FallbackChallengeGenerator(ChallengeGenerator):
    """Tries the primary generator and falls back to the second one if it fails."""

    def __init__(self, primary: ChallengeGenerator, fallback: ChallengeGenerator):
        self.primary = primary
        self.fallback = fallback

    def generate(self, brief: ChallengeBrief) -> list[Challenge]:
        try:
            return self.primary.generate(brief)
        except Exception:
            logger.exception("Primary challenge generator failed, using the fallback")
            return self.fallback.generate(brief)

    def warm_up(self) -> None:
        try:
            self.primary.warm_up()
        except Exception:
            logger.warning("Primary challenge generator could not warm up", exc_info=True)
