from tests.fakes import InMemoryWalkRepository
from tests.microadventures.object_mothers import a_challenge, a_walk
from microadventures.application.queries.find_progress.find_progress_query import FindProgressQuery
from microadventures.application.queries.find_progress.find_progress_query_handler import (
    FIRST_WALK_STICKER,
    PERFECT_WALK_STICKER,
    FindProgressQueryHandler,
)
from microadventures.domain.models.challenge_status import ChallengeStatus


def _completed():
    return a_challenge(status=ChallengeStatus.COMPLETED)


def test_it_returns_empty_progress_for_a_new_user():
    progress = FindProgressQueryHandler(InMemoryWalkRepository()).handle(FindProgressQuery(user_id="nobody"))

    assert (progress.walks_count, progress.challenges_completed, progress.stickers) == (0, 0, [])


def test_it_counts_completed_challenges_and_awards_stickers():
    repository = InMemoryWalkRepository()
    repository.save(a_walk(challenges=[_completed(), _completed()]))
    repository.save(a_walk(challenges=[_completed(), a_challenge()]))
    repository.save(a_walk(user_id="someone-else", challenges=[_completed()]))

    progress = FindProgressQueryHandler(repository).handle(FindProgressQuery(user_id="user-1"))

    assert progress.walks_count == 2
    assert progress.challenges_completed == 3
    assert progress.perfect_walks == 1
    assert progress.stickers == [FIRST_WALK_STICKER, PERFECT_WALK_STICKER]


def test_a_walk_with_swaps_is_not_perfect():
    repository = InMemoryWalkRepository()
    repository.save(a_walk(challenges=[_completed()], swaps_used=1))

    progress = FindProgressQueryHandler(repository).handle(FindProgressQuery(user_id="user-1"))

    assert progress.perfect_walks == 0
    assert progress.stickers == [FIRST_WALK_STICKER]
