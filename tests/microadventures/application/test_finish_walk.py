from uuid import uuid4

import pytest

from tests.fakes import InMemoryWalkRepository
from tests.microadventures.object_mothers import a_walk
from microadventures.application.commands.finish_walk.finish_walk_command import FinishWalkCommand
from microadventures.application.commands.finish_walk.finish_walk_command_handler import FinishWalkCommandHandler
from microadventures.domain.exceptions.walk_not_found_exception import WalkNotFoundException


def _repository_with(walk):
    repository = InMemoryWalkRepository()
    repository.save(walk)
    return repository


def test_it_saves_the_time_the_distance_and_the_story():
    walk = a_walk()
    repository = _repository_with(walk)

    FinishWalkCommandHandler(repository).handle(
        FinishWalkCommand(walk_id=walk.id, walked_minutes=50, distance_km=4.2, diary="  Vi el atardecer desde el puente.  ")
    )

    saved = repository.find_or_fail_by_id(walk.id)
    assert (saved.walked_minutes, saved.distance_km, saved.diary) == (50, 4.2, "Vi el atardecer desde el puente.")
    assert saved.is_finished


def test_everything_is_optional():
    walk = a_walk()
    repository = _repository_with(walk)

    FinishWalkCommandHandler(repository).handle(FinishWalkCommand(walk_id=walk.id))

    saved = repository.find_or_fail_by_id(walk.id)
    assert (saved.walked_minutes, saved.distance_km, saved.diary) == (None, None, "")
    assert saved.is_finished


def test_telling_it_again_replaces_what_was_said_before():
    walk = a_walk()
    repository = _repository_with(walk)
    handler = FinishWalkCommandHandler(repository)

    handler.handle(FinishWalkCommand(walk_id=walk.id, walked_minutes=20, diary="Primera versión"))
    handler.handle(FinishWalkCommand(walk_id=walk.id, walked_minutes=35, diary="Segunda versión"))

    saved = repository.find_or_fail_by_id(walk.id)
    assert (saved.walked_minutes, saved.diary) == (35, "Segunda versión")


def test_a_walk_that_was_not_finished_says_so():
    assert not a_walk().is_finished


def test_it_fails_when_the_walk_does_not_exist():
    with pytest.raises(WalkNotFoundException):
        FinishWalkCommandHandler(InMemoryWalkRepository()).handle(FinishWalkCommand(walk_id=uuid4()))
