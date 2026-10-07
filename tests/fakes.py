from copy import deepcopy
from uuid import UUID

from microadventures.domain.models.challenge import Challenge
from microadventures.domain.models.challenge_brief import ChallengeBrief
from microadventures.domain.services.challenge_generator import ChallengeGenerator
from microadventures.domain.exceptions.walk_not_found_exception import WalkNotFoundException
from microadventures.domain.models.photo_verdict import PhotoVerdict
from microadventures.domain.services.photo_verifier import PhotoVerifier
from microadventures.domain.services.walk_criteria import WalkCriteria
from microadventures.domain.services.walk_service import WalkService
from microadventures.domain.models.walk import Walk


class InMemoryWalkRepository(WalkService):
    """Stores copies, so a handler that forgets to call save() fails its test."""

    def __init__(self):
        self.walks: dict[UUID, Walk] = {}

    def save(self, walk: Walk) -> None:
        self.walks[walk.id] = deepcopy(walk)

    def find_by_criteria(self, criteria: WalkCriteria) -> list[Walk]:
        walks = self.walks.values()
        if criteria.id is not None:
            walks = [walk for walk in walks if walk.id == criteria.id]
        if criteria.user_id is not None:
            walks = [walk for walk in walks if walk.user_id == criteria.user_id]
        return [deepcopy(walk) for walk in walks]

    def find_or_fail_by_id(self, id: UUID) -> Walk:
        if id not in self.walks:
            raise WalkNotFoundException(id)
        return deepcopy(self.walks[id])


class StubChallengeGenerator(ChallengeGenerator):
    def __init__(self, challenges: list[Challenge]):
        self.challenges = challenges
        self.briefs: list[ChallengeBrief] = []

    def generate(self, brief: ChallengeBrief) -> list[Challenge]:
        self.briefs.append(brief)
        return self.challenges


class StubPhotoVerifier(PhotoVerifier):
    def __init__(self, verdict: PhotoVerdict = PhotoVerdict(accepted=True)):
        self.verdict = verdict
        self.verified: list[Challenge] = []

    def verify(self, challenge: Challenge, photo: bytes) -> PhotoVerdict:
        self.verified.append(challenge)
        return self.verdict
