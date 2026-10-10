import json

import pytest
from django.test import Client

from api import wiring
from api.auth.session import issue_tokens
from microadventures.domain.exceptions.weather_unavailable_exception import WeatherUnavailableException
from microadventures.infrastructure.template_challenge_generator import TemplateChallengeGenerator
from tests.auth_helpers import signed_in
from tests.fakes import InMemoryAccountRepository, InMemoryWalkRepository

LEGACY_ID = "5f0a8c1e-1111-4222-8333-944455556666"


@pytest.fixture(autouse=True)
def adapters(monkeypatch, settings):
    accounts, walks = InMemoryAccountRepository(), InMemoryWalkRepository()
    monkeypatch.setattr(wiring, "_account_repository", lambda: accounts)
    monkeypatch.setattr(wiring, "_walk_repository", lambda: walks)
    monkeypatch.setattr(wiring, "_challenge_generator", lambda: TemplateChallengeGenerator())
    settings.PHOTO_VERIFIER = "trusting"


def _post(client, url, body):
    return client.post(url, data=json.dumps(body), content_type="application/json")


def test_without_a_token_the_private_routes_answer_401():
    client = Client()

    assert client.get("/api/users/user-1/progress").status_code == 401
    assert _post(client, "/api/walks", {"user_id": "user-1", "mood": "calm"}).status_code == 401
    assert client.get("/api/context?latitude=1&longitude=1").status_code == 401
    assert client.post("/api/warmup").status_code == 401


def test_the_health_check_and_the_session_start_need_no_token():
    assert Client().get("/api/health").status_code == 200
    assert _post(Client(), "/api/auth/start", {}).status_code == 200


def test_a_new_browser_gets_an_id_and_tokens_that_work():
    session = _post(Client(), "/api/auth/start", {}).json()

    client = Client(HTTP_AUTHORIZATION=f"Bearer {session['access']}")
    assert client.get(f"/api/users/{session['user_id']}/progress").status_code == 200


def test_a_browser_that_already_had_an_id_keeps_its_data():
    session = _post(Client(), "/api/auth/start", {"user_id": LEGACY_ID}).json()

    assert session["user_id"] == LEGACY_ID


def test_an_id_can_start_a_session_only_once():
    _post(Client(), "/api/auth/start", {"user_id": LEGACY_ID})

    again = _post(Client(), "/api/auth/start", {"user_id": LEGACY_ID})

    assert again.status_code == 409


def test_a_strange_id_is_refused():
    assert _post(Client(), "/api/auth/start", {"user_id": "../../etc"}).status_code == 422


def test_nobody_reads_the_data_of_another_user():
    other = signed_in("user-2")

    assert other.get("/api/users/user-1/progress").status_code == 403
    assert other.get("/api/users/user-1/summary/weekly").status_code == 403
    assert other.get("/api/users/user-1/reminders").status_code == 403
    assert other.post("/api/users/user-1/telegram/link").status_code == 403


def test_a_walk_cannot_be_started_for_someone_else():
    response = _post(signed_in("user-2"), "/api/walks", {"user_id": "user-1", "mood": "calm"})

    assert response.status_code == 403


def test_a_walk_is_invisible_to_everyone_but_its_owner():
    walk_id = _post(signed_in("user-1"), "/api/walks", {"user_id": "user-1", "mood": "calm"}).json()["id"]

    intruder = signed_in("user-2")

    assert signed_in("user-1").get(f"/api/walks/{walk_id}").status_code == 200
    assert intruder.get(f"/api/walks/{walk_id}").status_code == 404
    assert _post(intruder, f"/api/walks/{walk_id}/finish", {}).status_code == 404
    assert intruder.post(f"/api/walks/{walk_id}/challenges/{walk_id}/swap").status_code == 404


def test_a_refresh_token_does_not_open_the_api():
    refresh = issue_tokens("user-1")["refresh"]

    client = Client(HTTP_AUTHORIZATION=f"Bearer {refresh}")

    assert client.get("/api/users/user-1/progress").status_code == 401


def test_a_refresh_token_gives_a_new_pair():
    refresh = issue_tokens("user-1")["refresh"]

    renewed = _post(Client(), "/api/auth/refresh", {"refresh": refresh})

    assert renewed.status_code == 200 and renewed.json()["user_id"] == "user-1"
    assert Client(HTTP_AUTHORIZATION=f"Bearer {renewed.json()['access']}").get("/api/users/user-1/progress").status_code == 200


def test_a_broken_refresh_token_is_refused():
    assert _post(Client(), "/api/auth/refresh", {"refresh": "nonsense"}).status_code == 401


def test_a_token_signed_with_another_key_is_refused(settings):
    token = issue_tokens("user-1")["access"]
    client = Client(HTTP_AUTHORIZATION=f"Bearer {token[:-4]}AAAA")

    assert client.get("/api/users/user-1/progress").status_code == 401


def test_the_api_documentation_is_not_published():
    assert Client().get("/api/docs").status_code == 404
    assert Client().get("/api/openapi.json").status_code == 404


def test_an_internal_failure_does_not_tell_what_failed(monkeypatch):
    class Failing:
        def handle(self, command):
            raise WeatherUnavailableException("api.met.no timeout key=abc")

    monkeypatch.setattr(wiring, "warm_up_generator_handler", lambda: Failing())

    response = signed_in().post("/api/warmup")

    assert response.status_code == 503
    assert response.json() == {"detail": "Service unavailable"}
