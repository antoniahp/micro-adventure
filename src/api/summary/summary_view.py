from datetime import date

from ninja import Router, Status

from api import wiring
from api.summary.summary_serializer import WeeklyReflectionIn, WeeklySummaryOut, YearlySummaryOut
from microadventures.application.commands.save_weekly_reflection.save_weekly_reflection_command import SaveWeeklyReflectionCommand
from microadventures.application.queries.find_weekly_summary.find_weekly_summary_query import FindWeeklySummaryQuery
from microadventures.application.queries.find_yearly_summary.find_yearly_summary_query import FindYearlySummaryQuery

router = Router()  # mounted at /users


@router.get("/{user_id}/summary/weekly", response=WeeklySummaryOut)
def get_weekly_summary(request, user_id: str, week: date | None = None, timezone: str = "UTC"):
    return wiring.find_weekly_summary_handler().handle(FindWeeklySummaryQuery(user_id=user_id, week=week, timezone=timezone))


@router.put("/{user_id}/summary/weekly/feeling", response={204: None})
def save_weekly_feeling(request, user_id: str, payload: WeeklyReflectionIn):
    """How the person says the week felt. Saying it again for the same week replaces it."""
    wiring.save_weekly_reflection_handler().handle(
        SaveWeeklyReflectionCommand(user_id=user_id, week=payload.week, feeling=payload.feeling, note=payload.note)
    )
    return Status(204, None)


@router.get("/{user_id}/summary/yearly", response=YearlySummaryOut)
def get_yearly_summary(request, user_id: str, year: int | None = None, timezone: str = "UTC"):
    return wiring.find_yearly_summary_handler().handle(FindYearlySummaryQuery(user_id=user_id, year=year, timezone=timezone))
