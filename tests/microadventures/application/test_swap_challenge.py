import pytest

from tests.fakes import InMemoryWalkRepository, StubChallengeGenerator
from tests.microadventures.object_mothers import a_challenge, a_walk
from microadventures.application.commands.swap_challenge.swap_challenge_command import SwapChallengeCommand
from microadventures.application.commands.swap_challenge.swap_challenge_command_handler import SwapChallengeCommandHandler
from microadventures.domain.models.challenge_category import ChallengeCategory
from microadventures.domain.models.challenge_status import ChallengeStatus
from microadventures.domain.exceptions.challenge_already_completed_exception import ChallengeAlreadyCompletedException
from microadventures.domain.exceptions.swap_limit_reached_exception import SwapLimitReachedException


def _setup(walk, replacement):
    repository = InMemoryWalkRepository()
    repository.save(walk)
    generator = StubChallengeGenerator([replacement])
    return repository, generator, SwapChallengeCommandHandler(repository, generator)


def test_it_replaces_the_challenge_with_one_of_the_same_category():
    current = a_challenge(category=ChallengeCategory.SOUND)
    replacement = a_challenge(category=ChallengeCategory.SOUND, text="Escucha una fuente.")
    walk = a_walk(challenges=[current])
    repository, generator, handler = _setup(walk, replacement)

    handler.handle(SwapChallengeCommand(walk_id=walk.id, challenge_id=current.id))

    saved = repository.find_or_fail_by_id(walk.id)
    assert saved.challenges == [replacement]
    assert saved.swaps_used == 1
    assert generator.briefs[0].category == ChallengeCategory.SOUND
    assert generator.briefs[0].count == 1


def test_it_refuses_a_swap_without_calling_the_generator_when_none_are_left():
    current = a_challenge()
    walk = a_walk(challenges=[current], swaps_used=2)
    _, generator, handler = _setup(walk, a_challenge())

    with pytest.raises(SwapLimitReachedException):
        handler.handle(SwapChallengeCommand(walk_id=walk.id, challenge_id=current.id))

    assert generator.briefs == []


def test_it_does_not_swap_a_completed_challenge():
    current = a_challenge(status=ChallengeStatus.COMPLETED)
    walk = a_walk(challenges=[current])
    _, _, handler = _setup(walk, a_challenge())

    with pytest.raises(ChallengeAlreadyCompletedException):
        handler.handle(SwapChallengeCommand(walk_id=walk.id, challenge_id=current.id))


def test_the_replacement_is_asked_for_with_what_the_person_wrote():
    current = a_challenge()
    walk = a_walk(challenges=[current], note="Quiero algo tranquilo")
    _, generator, handler = _setup(walk, a_challenge())

    handler.handle(SwapChallengeCommand(walk_id=walk.id, challenge_id=current.id))

    assert generator.briefs[0].note == "Quiero algo tranquilo"
