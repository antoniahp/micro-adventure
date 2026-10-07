from uuid import uuid4

import pytest

from tests.microadventures.object_mothers import a_challenge, a_walk
from microadventures.domain.models.challenge_status import ChallengeStatus
from microadventures.domain.exceptions.walk_not_found_exception import WalkNotFoundException
from microadventures.domain.services.walk_criteria import WalkCriteria
from microadventures.infrastructure.repositories.db_walk_repository import DbWalkRepository

# These tests talk to a real MongoDB (the compose service), so they are the only ones that need it.
pytestmark = pytest.mark.django_db(transaction=True)


def test_it_saves_and_finds_a_walk_by_id():
    repository = DbWalkRepository()
    walk = a_walk(challenges=[a_challenge(status=ChallengeStatus.COMPLETED)], swaps_used=1)

    repository.save(walk)
    found = repository.find_or_fail_by_id(walk.id)

    assert found.challenges == walk.challenges
    assert found.challenges[0].is_completed
    assert (found.user_id, found.mood, found.minutes, found.swaps_used) == (walk.user_id, walk.mood, 30, 1)
    assert found.created_at.tzinfo is not None


def test_saving_twice_updates_the_same_walk():
    repository = DbWalkRepository()
    walk = a_walk()
    repository.save(walk)

    walk.complete_challenge(walk.challenges[0].id)
    repository.save(walk)

    assert len(repository.find_by_criteria(WalkCriteria())) == 1
    assert repository.find_or_fail_by_id(walk.id).challenges[0].is_completed


def test_it_finds_walks_by_user():
    repository = DbWalkRepository()
    repository.save(a_walk(user_id="user-1"))
    repository.save(a_walk(user_id="user-1"))
    repository.save(a_walk(user_id="user-2"))

    assert len(repository.find_by_criteria(WalkCriteria(user_id="user-1"))) == 2


def test_it_fails_when_the_walk_does_not_exist():
    with pytest.raises(WalkNotFoundException):
        DbWalkRepository().find_or_fail_by_id(uuid4())
