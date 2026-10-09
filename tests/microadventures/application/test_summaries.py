from datetime import date, datetime, timezone

import pytest

from tests.fakes import InMemoryReflectionRepository, InMemoryWalkRepository
from tests.microadventures.object_mothers import a_challenge, a_walk
from microadventures.application.commands.save_weekly_reflection.save_weekly_reflection_command import SaveWeeklyReflectionCommand
from microadventures.application.commands.save_weekly_reflection.save_weekly_reflection_command_handler import SaveWeeklyReflectionCommandHandler
from microadventures.application.queries.find_progress.find_progress_query import FindProgressQuery
from microadventures.application.queries.find_progress.find_progress_query_handler import FindProgressQueryHandler
from microadventures.application.queries.find_weekly_summary.find_weekly_summary_query import FindWeeklySummaryQuery
from microadventures.application.queries.find_weekly_summary.find_weekly_summary_query_handler import FindWeeklySummaryQueryHandler
from microadventures.application.queries.find_yearly_summary.find_yearly_summary_query import FindYearlySummaryQuery
from microadventures.application.queries.find_yearly_summary.find_yearly_summary_query_handler import FindYearlySummaryQueryHandler
from microadventures.domain.exceptions.invalid_weekly_reflection_exception import InvalidWeeklyReflectionException
from microadventures.domain.models.challenge_category import ChallengeCategory
from microadventures.domain.models.challenge_status import ChallengeStatus
from microadventures.domain.models.mood import Mood


def at(year, month, day, hour=12):
    return datetime(year, month, day, hour, tzinfo=timezone.utc)


def done(**overrides):
    return a_challenge(status=ChallengeStatus.COMPLETED, **overrides)


def walk_on(day, **overrides):
    """A walk with one challenge completed, on the given (year, month, day)."""
    return a_walk(created_at=at(*day), challenges=[done()], **overrides)


# --- Stickers -------------------------------------------------------------------------------------------------------

def _book(repository, timezone_name="UTC"):
    progress = FindProgressQueryHandler(repository).handle(FindProgressQuery(user_id="user-1", timezone=timezone_name))
    return {s.code: s for s in progress.sticker_book}, progress


def test_every_sticker_shows_how_far_the_person_is_from_it():
    repository = InMemoryWalkRepository()
    for day in range(1, 4):
        repository.save(walk_on((2026, 10, day)))

    book, _ = _book(repository)

    assert (book["five_walks"].current, book["five_walks"].goal, book["five_walks"].unlocked) == (3, 5, False)
    assert book["first_walk"].unlocked and book["streak_3"].unlocked
    assert not book["streak_7"].unlocked and book["streak_7"].current == 3


def test_a_new_person_has_all_the_stickers_locked_and_at_zero():
    book, progress = _book(InMemoryWalkRepository())

    assert progress.stickers == []
    assert all(not s.unlocked and s.current == 0 for s in book.values())


def test_the_progress_never_goes_above_the_goal():
    repository = InMemoryWalkRepository()
    for day in range(1, 9):
        repository.save(walk_on((2026, 10, day)))

    book, _ = _book(repository)

    assert book["five_walks"].current == 5 and book["five_walks"].unlocked


def test_the_explorer_needs_every_category():
    repository = InMemoryWalkRepository()
    repository.save(a_walk(challenges=[done(category=c) for c in ChallengeCategory.values]))

    book, _ = _book(repository)

    assert book["all_categories"].unlocked


def test_stories_kilometres_and_minutes_count_for_their_stickers():
    repository = InMemoryWalkRepository()
    repository.save(a_walk(challenges=[done(story="Un gato") for _ in range(6)], diary="Un buen día", distance_km=10.4, walked_minutes=310))

    book, _ = _book(repository)

    assert book["storyteller"].current == 7
    assert book["ten_km"].unlocked and book["five_hours"].unlocked


def test_a_streak_needs_consecutive_days_in_the_persons_time_zone():
    repository = InMemoryWalkRepository()
    repository.save(a_walk(created_at=at(2026, 10, 1, 23), challenges=[done()]))  # 01:00 on the 2nd in Madrid
    repository.save(a_walk(created_at=at(2026, 10, 3, 10), challenges=[done()]))

    in_utc, _ = _book(repository, "UTC")
    in_madrid, _ = _book(repository, "Europe/Madrid")

    assert in_utc["streak_3"].current == 1  # 1st and 3rd: not in a row
    assert in_madrid["streak_3"].current == 2  # the 2nd and the 3rd


def test_a_walk_without_completed_challenges_does_not_make_a_streak():
    repository = InMemoryWalkRepository()
    repository.save(a_walk(created_at=at(2026, 10, 1), challenges=[a_challenge()]))

    book, progress = _book(repository)

    assert progress.walks_count == 1 and progress.days_walked == 0
    assert book["streak_3"].current == 0


# --- Weekly summary -------------------------------------------------------------------------------------------------

def _weekly(repository, reflections=None, **query):
    handler = FindWeeklySummaryQueryHandler(repository, reflections or InMemoryReflectionRepository())
    return handler.handle(FindWeeklySummaryQuery(user_id="user-1", **query))


def test_the_week_goes_from_monday_to_sunday_and_adds_up_what_happened():
    repository = InMemoryWalkRepository()
    repository.save(walk_on((2026, 10, 5), walked_minutes=30, distance_km=2.5, mood=Mood.TIRED))  # Monday
    repository.save(walk_on((2026, 10, 9), walked_minutes=45, distance_km=3.0, mood=Mood.ACTIVE))  # Friday
    repository.save(walk_on((2026, 10, 11)))  # Sunday
    repository.save(walk_on((2026, 10, 12)))  # next Monday: not in this week

    summary = _weekly(repository, week=date(2026, 10, 7))

    assert (summary.week_start, summary.week_end) == (date(2026, 10, 5), date(2026, 10, 11))
    assert (summary.walks_count, summary.days_walked, summary.challenges_completed) == (3, 3, 3)
    assert (summary.minutes, summary.km) == (75, 5.5)
    assert summary.moods == {"tired": 1, "active": 1, "calm": 1}
    assert [d.walks for d in summary.days] == [1, 0, 0, 0, 1, 0, 1]


def test_it_compares_with_the_week_before():
    repository = InMemoryWalkRepository()
    repository.save(walk_on((2026, 9, 30), walked_minutes=20))
    repository.save(walk_on((2026, 10, 6), walked_minutes=50))
    repository.save(walk_on((2026, 10, 7), walked_minutes=10))

    summary = _weekly(repository, week=date(2026, 10, 8))

    assert (summary.walks_count, summary.previous_walks) == (2, 1)
    assert (summary.minutes, summary.previous_minutes) == (60, 20)


def test_an_empty_week_is_an_empty_summary_not_an_error():
    summary = _weekly(InMemoryWalkRepository(), week=date(2026, 10, 8))

    assert summary.walks_count == 0 and summary.km == 0 and summary.feeling is None
    assert len(summary.days) == 7


def test_it_counts_the_categories_of_the_completed_challenges():
    repository = InMemoryWalkRepository()
    repository.save(a_walk(created_at=at(2026, 10, 6), challenges=[done(category=ChallengeCategory.SOUND), done(category=ChallengeCategory.SOUND), a_challenge()]))

    summary = _weekly(repository, week=date(2026, 10, 6))

    assert summary.categories == {"sound": 2}


def test_how_the_week_felt_is_saved_per_week_and_can_be_changed():
    reflections = InMemoryReflectionRepository()
    save = SaveWeeklyReflectionCommandHandler(reflections).handle

    save(SaveWeeklyReflectionCommand(user_id="user-1", week=date(2026, 10, 8), feeling=3, note="Regular"))
    save(SaveWeeklyReflectionCommand(user_id="user-1", week=date(2026, 10, 6), feeling=5, note=" Genial "))

    summary = _weekly(InMemoryWalkRepository(), reflections, week=date(2026, 10, 7))
    other_week = _weekly(InMemoryWalkRepository(), reflections, week=date(2026, 10, 14))

    assert (summary.feeling, summary.feeling_note) == (5, "Genial")
    assert other_week.feeling is None
    assert len(reflections.reflections) == 1


@pytest.mark.parametrize("feeling", [0, 6])
def test_a_feeling_outside_one_to_five_is_refused(feeling):
    with pytest.raises(InvalidWeeklyReflectionException):
        SaveWeeklyReflectionCommandHandler(InMemoryReflectionRepository()).handle(
            SaveWeeklyReflectionCommand(user_id="user-1", week=date(2026, 10, 7), feeling=feeling)
        )


# --- Yearly summary -------------------------------------------------------------------------------------------------

def _yearly(repository, reflections=None, **query):
    handler = FindYearlySummaryQueryHandler(repository, reflections or InMemoryReflectionRepository())
    return handler.handle(FindYearlySummaryQuery(user_id="user-1", **query))


def test_the_year_is_split_in_twelve_months():
    repository = InMemoryWalkRepository()
    repository.save(walk_on((2026, 1, 15), walked_minutes=30, distance_km=2.0))
    repository.save(walk_on((2026, 1, 20), walked_minutes=30, distance_km=1.5))
    repository.save(walk_on((2026, 12, 31)))
    repository.save(walk_on((2025, 6, 1)))  # another year

    summary = _yearly(repository, year=2026)

    assert len(summary.months) == 12
    assert (summary.months[0].walks, summary.months[0].minutes, summary.months[0].km) == (2, 60, 3.5)
    assert summary.months[11].walks == 1
    assert summary.walks_count == 3 and summary.best_month == 1
    assert 2025 in summary.years and 2026 in summary.years


def test_it_knows_the_busiest_weekday_and_the_longest_streak():
    repository = InMemoryWalkRepository()
    for day in (5, 6, 7, 8):  # Monday to Thursday
        repository.save(walk_on((2026, 10, day)))
    repository.save(walk_on((2026, 10, 12)))  # Monday

    summary = _yearly(repository, year=2026)

    assert summary.weekdays == [2, 1, 1, 1, 0, 0, 0]
    assert summary.longest_streak == 4


def test_the_average_feeling_of_each_month_comes_from_the_weekly_answers():
    reflections = InMemoryReflectionRepository()
    save = SaveWeeklyReflectionCommandHandler(reflections).handle
    save(SaveWeeklyReflectionCommand(user_id="user-1", week=date(2026, 3, 2), feeling=4))
    save(SaveWeeklyReflectionCommand(user_id="user-1", week=date(2026, 3, 9), feeling=5))

    summary = _yearly(InMemoryWalkRepository(), reflections, year=2026)

    assert summary.months[2].feeling == 4.5
    assert summary.months[0].feeling is None


def test_an_empty_year_has_no_best_month():
    summary = _yearly(InMemoryWalkRepository(), year=2026)

    assert summary.best_month is None and summary.walks_count == 0 and summary.longest_streak == 0
