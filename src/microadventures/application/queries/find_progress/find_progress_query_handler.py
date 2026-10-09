from datetime import datetime

from microadventures.application.queries.find_progress.find_progress_query import FindProgressQuery
from microadventures.application.queries.find_progress.progress import Progress
from microadventures.domain.models.sticker import sticker_book
from microadventures.domain.models.walk_history import WalkHistory, zone_or_utc
from microadventures.domain.services.walk_criteria import WalkCriteria
from microadventures.domain.services.walk_service import WalkService

FIRST_WALK_STICKER = "first_walk"
PERFECT_WALK_STICKER = "perfect_walk"


class FindProgressQueryHandler:
    def __init__(self, walk_service: WalkService):
        self.walk_service = walk_service

    def handle(self, query: FindProgressQuery) -> Progress:
        zone = zone_or_utc(query.timezone)
        history = WalkHistory(self.walk_service.find_by_criteria(WalkCriteria(user_id=query.user_id)), zone)
        book = sticker_book(history.metrics())

        return Progress(
            walks_count=history.walks_count,
            days_walked=len(history.active_days),
            challenges_completed=history.challenges_completed,
            perfect_walks=history.perfect_walks,
            stickers=[s.code for s in book if s.unlocked],
            sticker_book=book,
            current_streak=history.current_streak(datetime.now(zone).date()),
        )
