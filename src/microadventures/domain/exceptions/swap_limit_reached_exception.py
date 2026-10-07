from uuid import UUID


class SwapLimitReachedException(Exception):
    def __init__(self, walk_id: UUID):
        super().__init__(f"Walk {walk_id} has no swaps left")
