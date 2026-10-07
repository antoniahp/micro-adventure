from uuid import uuid4

import pytest

from tests.fakes import InMemoryWalkRepository, StubPhotoVerifier
from tests.microadventures.object_mothers import a_challenge, a_walk
from microadventures.application.commands.complete_challenge.complete_challenge_command import CompleteChallengeCommand
from microadventures.application.commands.complete_challenge.complete_challenge_command_handler import CompleteChallengeCommandHandler
from microadventures.domain.models.challenge_category import ChallengeCategory
from microadventures.domain.exceptions.challenge_not_found_exception import ChallengeNotFoundException
from microadventures.domain.exceptions.photo_rejected_exception import PhotoRejectedException
from microadventures.domain.exceptions.challenge_response_required_exception import ChallengeResponseRequiredException
from microadventures.domain.models.photo_verdict import PhotoVerdict


def _repository_with(walk):
    repository = InMemoryWalkRepository()
    repository.save(walk)
    return repository


def test_it_completes_a_challenge_when_the_photo_is_accepted():
    challenge = a_challenge()
    walk = a_walk(challenges=[challenge])
    repository = _repository_with(walk)

    CompleteChallengeCommandHandler(repository, StubPhotoVerifier()).handle(
        CompleteChallengeCommand(walk_id=walk.id, challenge_id=challenge.id, photo=b"photo")
    )

    assert repository.find_or_fail_by_id(walk.id).challenges[0].is_completed


def test_it_rejects_the_challenge_when_the_photo_does_not_match():
    challenge = a_challenge()
    walk = a_walk(challenges=[challenge])
    repository = _repository_with(walk)
    verifier = StubPhotoVerifier(PhotoVerdict(accepted=False, reason="no se ve ningún árbol"))

    with pytest.raises(PhotoRejectedException):
        CompleteChallengeCommandHandler(repository, verifier).handle(
            CompleteChallengeCommand(walk_id=walk.id, challenge_id=challenge.id, photo=b"photo")
        )

    assert not repository.find_or_fail_by_id(walk.id).challenges[0].is_completed


def test_it_requires_a_photo_or_a_story():
    challenge = a_challenge()
    walk = a_walk(challenges=[challenge])

    with pytest.raises(ChallengeResponseRequiredException):
        CompleteChallengeCommandHandler(_repository_with(walk), StubPhotoVerifier()).handle(
            CompleteChallengeCommand(walk_id=walk.id, challenge_id=challenge.id)
        )


def test_it_completes_a_challenge_with_a_story_and_no_photo():
    challenge = a_challenge()
    walk = a_walk(challenges=[challenge])
    repository = _repository_with(walk)
    verifier = StubPhotoVerifier()

    CompleteChallengeCommandHandler(repository, verifier).handle(
        CompleteChallengeCommand(
            walk_id=walk.id, challenge_id=challenge.id, story="  Una hoja de plátano, áspera y fría.  "
        )
    )

    completed = repository.find_or_fail_by_id(walk.id).challenges[0]
    assert completed.is_completed
    assert completed.story == "Una hoja de plátano, áspera y fría."
    assert verifier.verified == []


def test_it_refuses_a_story_that_is_too_short():
    challenge = a_challenge()
    walk = a_walk(challenges=[challenge])

    with pytest.raises(ChallengeResponseRequiredException):
        CompleteChallengeCommandHandler(_repository_with(walk), StubPhotoVerifier()).handle(
            CompleteChallengeCommand(walk_id=walk.id, challenge_id=challenge.id, story="vale")
        )


def test_people_watching_challenges_are_answered_by_telling_never_with_a_photo():
    challenge = a_challenge(category=ChallengeCategory.PEOPLE_WATCHING)
    walk = a_walk(challenges=[challenge])
    repository = _repository_with(walk)
    verifier = StubPhotoVerifier()

    with pytest.raises(ChallengeResponseRequiredException):
        CompleteChallengeCommandHandler(repository, verifier).handle(
            CompleteChallengeCommand(walk_id=walk.id, challenge_id=challenge.id, photo=b"photo")
        )

    CompleteChallengeCommandHandler(repository, verifier).handle(
        CompleteChallengeCommand(
            walk_id=walk.id, challenge_id=challenge.id, story="Dos chicos riendo con un helado enorme."
        )
    )

    assert repository.find_or_fail_by_id(walk.id).challenges[0].is_completed
    assert verifier.verified == []


def test_it_fails_when_the_challenge_is_not_in_the_walk():
    walk = a_walk()

    with pytest.raises(ChallengeNotFoundException):
        CompleteChallengeCommandHandler(_repository_with(walk), StubPhotoVerifier()).handle(
            CompleteChallengeCommand(walk_id=walk.id, challenge_id=uuid4(), photo=b"photo")
        )
