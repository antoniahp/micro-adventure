from uuid import uuid4

from tests.fakes import InMemoryWalkRepository, StubChallengeGenerator
from tests.microadventures.object_mothers import a_challenge
from microadventures.application.commands.start_walk.start_walk_command import StartWalkCommand
from microadventures.application.commands.start_walk.start_walk_command_handler import StartWalkCommandHandler
from microadventures.domain.models.mood import Mood


def test_it_saves_a_walk_with_the_generated_challenges():
    challenges = [a_challenge(), a_challenge()]
    repository = InMemoryWalkRepository()
    generator = StubChallengeGenerator(challenges)
    walk_id = uuid4()

    StartWalkCommandHandler(repository, generator).handle(
        StartWalkCommand(
            walk_id=walk_id, user_id="user-1", mood=Mood.TIRED, minutes=20, weather="rain", challenges_count=2
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
            walk_id=uuid4(), user_id="user-1", mood=Mood.ACTIVE, minutes=45, weather="clear", challenges_count=1
        )
    )

    brief = generator.briefs[0]
    assert (brief.mood, brief.minutes, brief.weather, brief.count) == (Mood.ACTIVE, 45, "clear", 1)


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
            challenges_count=1,
            note="Día de reuniones, necesito desconectar",
        )
    )

    assert generator.briefs[0].note == "Día de reuniones, necesito desconectar"
    assert repository.find_or_fail_by_id(walk_id).note == "Día de reuniones, necesito desconectar"
