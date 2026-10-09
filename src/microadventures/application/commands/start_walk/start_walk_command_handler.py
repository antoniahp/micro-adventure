import logging
from datetime import datetime, timezone

from microadventures.domain.exceptions.invalid_challenges_count_exception import InvalidChallengesCountException
from microadventures.domain.exceptions.weather_unavailable_exception import WeatherUnavailableException
from microadventures.domain.models.challenge_brief import ChallengeBrief
from microadventures.domain.models.conditions import Conditions
from microadventures.domain.models.walk_length import WalkLength
from microadventures.domain.services.challenge_generator import ChallengeGenerator
from microadventures.domain.services.walk_service import WalkService
from microadventures.domain.services.weather_service import WeatherService
from microadventures.domain.models.walk import Walk

from microadventures.application.commands.start_walk.start_walk_command import StartWalkCommand

logger = logging.getLogger(__name__)


class StartWalkCommandHandler:
    def __init__(self, walk_service: WalkService, challenge_generator: ChallengeGenerator, weather_service: WeatherService | None = None):
        self.walk_service = walk_service
        self.challenge_generator = challenge_generator
        self.weather_service = weather_service

    def handle(self, command: StartWalkCommand) -> None:
        count = self._challenges_count(command)
        conditions = self._conditions(command)
        brief = ChallengeBrief(
            mood=command.mood,
            minutes=command.minutes,
            weather=command.weather,
            count=count,
            note=command.note,
            language=command.language,
            conditions=conditions,
        )
        walk = Walk(
            id=command.walk_id,
            user_id=command.user_id,
            mood=command.mood,
            minutes=command.minutes,
            weather=command.weather,
            note=command.note,
            language=command.language,
            conditions=conditions.to_text(),
            challenges=self.challenge_generator.generate(brief),
        )
        self.walk_service.save(walk)

    def _conditions(self, command: StartWalkCommand) -> Conditions:
        """What the weather and the hour ask of this walk. Without a place, or if the weather fails, nothing special."""
        if self.weather_service is None or command.latitude is None or command.longitude is None:
            return Conditions()
        now = command.now or datetime.now(timezone.utc)
        try:
            return Conditions.from_weather(self.weather_service.at(command.latitude, command.longitude), now)
        except WeatherUnavailableException as error:
            logger.warning("Walk without weather: %s", error)
            return Conditions()

    @staticmethod
    def _challenges_count(command: StartWalkCommand) -> int:
        length = WalkLength.for_minutes(command.minutes)
        if command.challenges_count is None:
            return length.default
        if not length.accepts(command.challenges_count):
            raise InvalidChallengesCountException(
                command.minutes, command.challenges_count, length.minimum, length.maximum
            )
        return command.challenges_count
