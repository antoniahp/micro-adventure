class ChallengeGenerationFailedException(Exception):
    def __init__(self, reason: str):
        super().__init__(f"Could not generate challenges: {reason}")
