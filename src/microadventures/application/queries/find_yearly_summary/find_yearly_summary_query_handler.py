from datetime import date, datetime

from microadventures.application.queries.find_yearly_summary.find_yearly_summary_query import FindYearlySummaryQuery
from microadventures.application.queries.find_yearly_summary.yearly_summary import MonthSummary, YearlySummary
from microadventures.domain.models.walk_history import WalkHistory, zone_or_utc
from microadventures.domain.services.reflection_service import ReflectionService
from microadventures.domain.services.walk_criteria import WalkCriteria
from microadventures.domain.services.walk_service import WalkService


class FindYearlySummaryQueryHandler:
    def __init__(self, walk_service: WalkService, reflection_service: ReflectionService):
        self.walk_service = walk_service
        self.reflection_service = reflection_service

    def handle(self, query: FindYearlySummaryQuery) -> YearlySummary:
        zone = zone_or_utc(query.timezone)
        everything = WalkHistory(self.walk_service.find_by_criteria(WalkCriteria(user_id=query.user_id)), zone)
        today = datetime.now(zone).date()
        year = query.year or today.year
        history = everything.between(date(year, 1, 1), date(year + 1, 1, 1))

        feelings: dict[int, list[int]] = {}
        for reflection in self.reflection_service.find_by_user_id(query.user_id):
            if reflection.week_start.year == year:
                feelings.setdefault(reflection.week_start.month, []).append(reflection.feeling)

        months = []
        for month in range(1, 13):
            end = date(year + (month == 12), month % 12 + 1, 1)
            of_month = history.between(date(year, month, 1), end)
            answers = feelings.get(month)
            months.append(
                MonthSummary(
                    month=month,
                    walks=of_month.walks_count,
                    challenges=of_month.challenges_completed,
                    minutes=of_month.minutes,
                    km=of_month.km,
                    feeling=round(sum(answers) / len(answers), 1) if answers else None,
                )
            )

        busiest = max(months, key=lambda m: (m.challenges, m.walks))
        years = sorted({everything.day_of(w).year for w in everything.walks} | {today.year}, reverse=True)
        return YearlySummary(
            year=year,
            years=years,
            walks_count=history.walks_count,
            days_walked=len(history.active_days),
            challenges_completed=history.challenges_completed,
            perfect_walks=history.perfect_walks,
            minutes=history.minutes,
            km=history.km,
            stories=history.stories,
            longest_streak=history.longest_streak(),
            best_month=busiest.month if (busiest.challenges or busiest.walks) else None,
            months=months,
            moods=dict(history.moods),
            categories=dict(history.categories),
            weekdays=history.walks_per_weekday(),
        )
