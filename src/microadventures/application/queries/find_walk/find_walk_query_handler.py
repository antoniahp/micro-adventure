from microadventures.domain.services.walk_service import WalkService
from microadventures.domain.models.walk import Walk

from microadventures.application.queries.find_walk.find_walk_query import FindWalkQuery


class FindWalkQueryHandler:
    def __init__(self, walk_service: WalkService):
        self.walk_service = walk_service

    def handle(self, query: FindWalkQuery) -> Walk:
        return self.walk_service.find_or_fail_by_id(query.walk_id)
