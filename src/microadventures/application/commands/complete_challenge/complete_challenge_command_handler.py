from microadventures.domain.exceptions.challenge_response_required_exception import ChallengeResponseRequiredException
from microadventures.domain.exceptions.photo_rejected_exception import PhotoRejectedException
from microadventures.domain.services.photo_verifier import PhotoVerifier
from microadventures.domain.services.walk_service import WalkService

from microadventures.application.commands.complete_challenge.complete_challenge_command import CompleteChallengeCommand

MIN_STORY_LENGTH = 10


class CompleteChallengeCommandHandler:
    """A challenge is completed by telling something about it, by a photo that matches it, or both."""

    def __init__(self, walk_service: WalkService, photo_verifier: PhotoVerifier):
        self.walk_service = walk_service
        self.photo_verifier = photo_verifier

    def handle(self, command: CompleteChallengeCommand) -> None:
        walk = self.walk_service.find_or_fail_by_id(command.walk_id)
        challenge = walk.find_challenge(command.challenge_id)

        story = command.story.strip()
        photo = command.photo if challenge.accepts_photo else None
        if photo is None and len(story) < MIN_STORY_LENGTH:
            raise ChallengeResponseRequiredException(challenge.id, MIN_STORY_LENGTH)

        if photo is not None:
            verdict = self.photo_verifier.verify(challenge, photo)
            if not verdict.accepted:
                raise PhotoRejectedException(verdict.reason)

        walk.complete_challenge(challenge.id, story, with_photo=photo is not None)
        self.walk_service.save(walk)
