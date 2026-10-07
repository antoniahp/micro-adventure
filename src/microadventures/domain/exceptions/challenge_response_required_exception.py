from uuid import UUID


class ChallengeResponseRequiredException(Exception):
    def __init__(self, challenge_id: UUID, min_story_length: int):
        super().__init__(
            f"Challenge {challenge_id} needs a photo or a story of at least {min_story_length} characters"
        )
