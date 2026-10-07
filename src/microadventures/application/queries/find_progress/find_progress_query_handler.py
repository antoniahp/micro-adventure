from microadventures.domain.services.walk_criteria import WalkCriteria
from microadventures.domain.services.walk_service import WalkService

from microadventures.application.queries.find_progress.find_progress_query import FindProgressQuery
from microadventures.application.queries.find_progress.progress import Progress

FIRST_WALK_STICKER = "first_walk"
PERFECT_WALK_STICKER = "perfect_walk"


class FindProgressQueryHandler:
    def __init__(self, walk_service: WalkService):
        self.walk_service = walk_service

    def handle(self, query: FindProgressQuery) -> Progress:
        walks = self.walk_service.find_by_criteria(WalkCriteria(user_id=query.user_id))
        walks_with_progress = [walk for walk in walks if any(c.is_completed for c in walk.challenges)]

        challenges_completed = sum(1 for walk in walks for c in walk.challenges if c.is_completed)
        days_walked = {walk.created_at.date() for walk in walks_with_progress}
        perfect_walks = sum(1 for walk in walks if walk.is_perfect)

        stickers = []
        if walks_with_progress:
            stickers.append(FIRST_WALK_STICKER)
        if perfect_walks:
            stickers.append(PERFECT_WALK_STICKER)

        return Progress(
            walks_count=len(walks),
            days_walked=len(days_walked),
            challenges_completed=challenges_completed,
            perfect_walks=perfect_walks,
            stickers=stickers,
        )
