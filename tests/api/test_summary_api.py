import json
from datetime import datetime, timezone

import pytest
from tests.auth_helpers import signed_in

from api import wiring
from tests.fakes import InMemoryReflectionRepository, InMemoryWalkRepository
from tests.microadventures.object_mothers import a_challenge, a_walk
from microadventures.domain.models.challenge_status import ChallengeStatus


@pytest.fixture(autouse=True)
def adapters(monkeypatch):
    walks, reflections = InMemoryWalkRepository(), InMemoryReflectionRepository()
    monkeypatch.setattr(wiring, "_walk_repository", lambda: walks)
    monkeypatch.setattr(wiring, "_reflection_repository", lambda: reflections)
    walks.save(a_walk(created_at=datetime(2026, 10, 6, 10, tzinfo=timezone.utc), walked_minutes=40, distance_km=3.2, challenges=[a_challenge(status=ChallengeStatus.COMPLETED)]))
    return walks


def test_the_progress_includes_the_sticker_book_with_its_goals():
    body = signed_in().get("/api/users/user-1/progress?timezone=Europe/Madrid").json()

    five_walks = next(s for s in body["sticker_book"] if s["code"] == "five_walks")
    assert (five_walks["current"], five_walks["goal"], five_walks["unlocked"]) == (1, 5, False)
    assert body["stickers"] == ["first_walk", "perfect_walk"]  # its only challenge is done, with no swaps


def test_the_weekly_summary_adds_up_the_week():
    body = signed_in().get("/api/users/user-1/summary/weekly?week=2026-10-08&timezone=Europe/Madrid").json()

    assert body["week_start"] == "2026-10-05" and body["week_end"] == "2026-10-11"
    assert (body["walks_count"], body["minutes"], body["km"]) == (1, 40, 3.2)
    assert len(body["days"]) == 7 and body["feeling"] is None


def test_how_the_week_felt_is_saved_and_comes_back_in_the_summary():
    client = signed_in()

    saved = client.put(
        "/api/users/user-1/summary/weekly/feeling",
        data=json.dumps({"week": "2026-10-08", "feeling": 4, "note": "Bien"}),
        content_type="application/json",
    )
    body = client.get("/api/users/user-1/summary/weekly?week=2026-10-06").json()

    assert saved.status_code == 204
    assert (body["feeling"], body["feeling_note"]) == (4, "Bien")


@pytest.mark.parametrize("feeling", [0, 6])
def test_a_feeling_out_of_range_is_refused(feeling):
    response = signed_in().put(
        "/api/users/user-1/summary/weekly/feeling",
        data=json.dumps({"week": "2026-10-08", "feeling": feeling}),
        content_type="application/json",
    )

    assert response.status_code == 422


def test_the_yearly_summary_has_twelve_months():
    body = signed_in().get("/api/users/user-1/summary/yearly?year=2026&timezone=Europe/Madrid").json()

    assert len(body["months"]) == 12 and body["months"][9]["walks"] == 1
    assert body["walks_count"] == 1 and body["best_month"] == 10 and 2026 in body["years"]


def test_an_unknown_time_zone_does_not_break_the_summaries():
    assert signed_in().get("/api/users/user-1/summary/yearly?year=2026&timezone=Mars/Olympus").status_code == 200
