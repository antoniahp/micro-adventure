class InvalidChallengesCountException(Exception):
    def __init__(self, minutes: int, count: int, minimum: int, maximum: int):
        super().__init__(f"A walk of {minutes} minutes has {minimum} to {maximum} challenges, not {count}")
