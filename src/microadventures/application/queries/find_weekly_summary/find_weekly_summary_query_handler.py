from datetime import datetime, timedelta

from microadventures.application.queries.find_weekly_summary.find_weekly_summary_query import FindWeeklySummaryQuery
from microadventures.application.queries.find_weekly_summary.weekly_summary import DaySummary, WeeklySummary
from microadventures.domain.models.walk_history import WalkHistory, monday_of, zone_or_utc
from microadventures.domain.services.reflection_service import ReflectionService
from microadventures.domain.services.walk_criteria import WalkCriteria
from microadventures.domain.services.walk_service import WalkService


class FindWeeklySummaryQueryHandler:
    def __init__(self, walk_service: WalkService, reflection_service: ReflectionService):
        self.walk_service = walk_service
        self.reflection_service = reflection_service

    def handle(self, query: FindWeeklySummaryQuery) -> WeeklySummary:
        zone = zone_or_utc(query.timezone)
        history = WalkHistory(self.walk_service.find_by_criteria(WalkCriteria(user_id=query.user_id)), zone)
        start = monday_of(query.week or datetime.now(zone).date())
        end = start + timedelta(days=7)
        week = history.between(start, end)
        before = history.between(start - timedelta(days=7), start)

        days = []
        for offset in range(7):
            day = start + timedelta(days=offset)
            of_day = history.between(day, day + timedelta(days=1))
            days.append(DaySummary(day=day, walks=of_day.walks_count, challenges=of_day.challenges_completed))

        reflection = self.reflection_service.find_by_week(query.user_id, start)
        return WeeklySummary(
            week_start=start,
            week_end=end - timedelta(days=1),
            walks_count=week.walks_count,
            days_walked=len(week.active_days),
            challenges_completed=week.challenges_completed,
            perfect_walks=week.perfect_walks,
            minutes=week.minutes,
            km=week.km,
            stories=week.stories,
            days=days,
            moods=dict(week.moods),
            categories=dict(week.categories),
            previous_walks=before.walks_count,
            previous_challenges=before.challenges_completed,
            previous_minutes=before.minutes,
            previous_km=before.km,
            feeling=reflection.feeling if reflection else None,
            feeling_note=reflection.note if reflection else "",
        )
