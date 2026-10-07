from uuid import UUID


class ChallengeAlreadyCompletedException(Exception):
    def __init__(self, challenge_id: UUID):
        super().__init__(f"Challenge {challenge_id} is already completed and cannot be swapped")
