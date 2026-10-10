import json

import pytest
from django.core.cache import cache
from django.test import Client, override_settings

from api import wiring
from microadventures.infrastructure.template_challenge_generator import TemplateChallengeGenerator
from tests.auth_helpers import signed_in
from tests.fakes import InMemoryWalkRepository


@pytest.fixture(autouse=True)
def in_memory_adapters(monkeypatch, settings):
    repository = InMemoryWalkRepository()
    monkeypatch.setattr(wiring, "_walk_repository", lambda: repository)
    monkeypatch.setattr(wiring, "_challenge_generator", lambda: TemplateChallengeGenerator())
    settings.PHOTO_VERIFIER = "trusting"


def test_the_app_cannot_be_framed_by_another_site():
    assert Client().get("/api/health").headers["X-Frame-Options"] == "DENY"


def test_an_unknown_url_answers_generic_json_not_a_django_page():
    response = Client().get("/not-a-real-route")

    assert response.status_code == 404
    assert response.json() == {"detail": "Not found"}
    assert response["Content-Type"].startswith("application/json")


def test_a_story_over_the_limit_is_refused():
    client = signed_in()
    walk_id = client.post("/api/walks", data=json.dumps({"user_id": "user-1", "mood": "calm"}), content_type="application/json").json()["id"]
    challenge_id = client.get(f"/api/walks/{walk_id}").json()["challenges"][0]["id"]

    response = client.post(f"/api/walks/{walk_id}/challenges/{challenge_id}/complete", {"story": "x" * 2001})

    assert response.status_code == 422


def test_a_photo_over_the_limit_is_refused():
    from django.core.files.uploadedfile import SimpleUploadedFile

    client = signed_in()
    walk_id = client.post("/api/walks", data=json.dumps({"user_id": "user-1", "mood": "calm"}), content_type="application/json").json()["id"]
    challenge_id = next(c for c in client.get(f"/api/walks/{walk_id}").json()["challenges"] if c["accepts_photo"])["id"]
    huge = SimpleUploadedFile("tree.jpg", b"x" * (5 * 1024 * 1024 + 1), content_type="image/jpeg")

    response = client.post(f"/api/walks/{walk_id}/challenges/{challenge_id}/complete", {"photo": huge})

    assert response.status_code == 422


def test_a_declared_body_too_large_is_refused_before_it_is_read():
    response = Client().post(
        "/api/auth/start", data=json.dumps({"user_id": "x"}), content_type="application/json",
        **{"CONTENT_LENGTH": str(9 * 1024 * 1024)},
    )

    assert response.status_code == 413


@override_settings(RATE_LIMIT_ENABLED=True, RATE_LIMITS={"model": (2, 60), "default": (3, 60)})
def test_too_many_requests_from_the_same_address_are_refused():
    cache.clear()
    client = Client()

    for _ in range(3):
        allowed = client.get("/api/health")
    refused = client.get("/api/health")

    assert allowed.status_code == 200
    assert refused.status_code == 429
    assert "Retry-After" in refused.headers


@override_settings(RATE_LIMIT_ENABLED=True, RATE_LIMITS={"model": (1, 60), "default": (50, 60)})
def test_the_model_routes_have_a_tighter_budget():
    cache.clear()
    client = signed_in()

    first = client.post("/api/walks", data=json.dumps({"user_id": "user-1", "mood": "calm"}), content_type="application/json")
    second = client.post("/api/walks", data=json.dumps({"user_id": "user-1", "mood": "calm"}), content_type="application/json")

    assert first.status_code == 201
    assert second.status_code == 429
