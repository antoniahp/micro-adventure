from uuid import UUID


class ChallengeNotFoundException(Exception):
    def __init__(self, walk_id: UUID, challenge_id: UUID):
        super().__init__(f"Could not find challenge {challenge_id} in walk {walk_id}")
