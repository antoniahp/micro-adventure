from uuid import UUID


class WalkNotFoundException(Exception):
    def __init__(self, id: UUID):
        super().__init__(f"Could not find walk with ID {id}")
