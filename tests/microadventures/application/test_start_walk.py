from uuid import uuid4

import pytest

from tests.fakes import InMemoryWalkRepository, StubChallengeGenerator
from tests.microadventures.object_mothers import a_challenge
from microadventures.application.commands.start_walk.start_walk_command import StartWalkCommand
from microadventures.application.commands.start_walk.start_walk_command_handler import StartWalkCommandHandler
from microadventures.domain.exceptions.invalid_challenges_count_exception import InvalidChallengesCountException
from microadventures.domain.models.language import Language
from microadventures.domain.models.mood import Mood


def test_it_saves_a_walk_with_the_generated_challenges():
    challenges = [a_challenge(), a_challenge()]
    repository = InMemoryWalkRepository()
    generator = StubChallengeGenerator(challenges)
    walk_id = uuid4()

    StartWalkCommandHandler(repository, generator).handle(
        StartWalkCommand(
            walk_id=walk_id, user_id="user-1", mood=Mood.TIRED, minutes=20, weather="rain", challenges_count=3
        )
    )

    walk = repository.find_or_fail_by_id(walk_id)
    assert walk.challenges == challenges
    assert walk.mood == Mood.TIRED
    assert walk.swaps_used == 0


def test_it_asks_the_generator_for_the_requested_context():
    generator = StubChallengeGenerator([a_challenge()])

    StartWalkCommandHandler(InMemoryWalkRepository(), generator).handle(
        StartWalkCommand(
            walk_id=uuid4(), user_id="user-1", mood=Mood.ACTIVE, minutes=45, weather="clear", challenges_count=5
        )
    )

    brief = generator.briefs[0]
    assert (brief.mood, brief.minutes, brief.weather, brief.count) == (Mood.ACTIVE, 45, "clear", 5)


def test_it_passes_what_the_person_wrote_to_the_generator_and_keeps_it_in_the_walk():
    repository, generator = InMemoryWalkRepository(), StubChallengeGenerator([a_challenge()])
    walk_id = uuid4()

    StartWalkCommandHandler(repository, generator).handle(
        StartWalkCommand(
            walk_id=walk_id,
            user_id="user-1",
            mood=Mood.TIRED,
            minutes=20,
            weather="rain",
            challenges_count=3,
            note="Día de reuniones, necesito desconectar",
        )
    )

    assert generator.briefs[0].note == "Día de reuniones, necesito desconectar"
    assert repository.find_or_fail_by_id(walk_id).note == "Día de reuniones, necesito desconectar"


def test_it_keeps_the_language_and_asks_the_generator_to_use_it():
    repository, generator = InMemoryWalkRepository(), StubChallengeGenerator([a_challenge()])
    walk_id = uuid4()

    StartWalkCommandHandler(repository, generator).handle(
        StartWalkCommand(
            walk_id=walk_id, user_id="user-1", mood=Mood.CALM, minutes=20, weather="clear", challenges_count=3,
            language=Language.EN,
        )
    )

    assert generator.briefs[0].language == Language.EN
    assert repository.find_or_fail_by_id(walk_id).language == Language.EN


def _start(minutes, challenges_count=None):
    generator = StubChallengeGenerator([a_challenge()])
    StartWalkCommandHandler(InMemoryWalkRepository(), generator).handle(
        StartWalkCommand(
            walk_id=uuid4(), user_id="user-1", mood=Mood.CALM, minutes=minutes, weather="clear",
            challenges_count=challenges_count,
        )
    )
    return generator.briefs[0]


@pytest.mark.parametrize("minutes, expected", [(15, 3), (30, 3), (45, 5), (59, 5), (60, 6), (90, 6)])
def test_it_asks_for_the_usual_number_of_challenges_for_the_time(minutes, expected):
    assert _start(minutes).count == expected


@pytest.mark.parametrize("count", [6, 8, 10])
def test_with_an_hour_or_more_the_person_chooses_between_6_and_10(count):
    assert _start(60, count).count == count


@pytest.mark.parametrize("minutes, count", [(30, 5), (45, 3), (45, 6), (60, 5), (60, 11)])
def test_it_refuses_a_number_of_challenges_that_does_not_fit_the_time(minutes, count):
    with pytest.raises(InvalidChallengesCountException):
        _start(minutes, count)
