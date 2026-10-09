import json
from uuid import uuid4

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client

from api import wiring
from tests.fakes import InMemoryWalkRepository
from microadventures.infrastructure.template_challenge_generator import TemplateChallengeGenerator


@pytest.fixture(autouse=True)
def in_memory_adapters(monkeypatch, settings):
    repository = InMemoryWalkRepository()
    monkeypatch.setattr(wiring, "_walk_repository", lambda: repository)
    monkeypatch.setattr(wiring, "_challenge_generator", lambda: TemplateChallengeGenerator())
    settings.PHOTO_VERIFIER = "trusting"


def _post_json(client, url, body):
    return client.post(url, data=json.dumps(body), content_type="application/json")


def test_a_user_walks_completes_a_challenge_and_sees_progress():
    client = Client()

    created = _post_json(client, "/api/walks", {"user_id": "user-1", "mood": "calm", "challenges_count": 2})
    assert created.status_code == 201
    walk_id = created.json()["id"]

    walk = client.get(f"/api/walks/{walk_id}").json()
    assert len(walk["challenges"]) == 2
    challenge = next(c for c in walk["challenges"] if c["accepts_photo"])

    photo = SimpleUploadedFile("tree.jpg", b"fake-image", content_type="image/jpeg")
    completed = client.post(f"/api/walks/{walk_id}/challenges/{challenge['id']}/complete", {"photo": photo})
    assert completed.status_code == 204

    progress = client.get("/api/users/user-1/progress").json()
    assert progress["walks_count"] == 1
    assert progress["challenges_completed"] == 1
    assert progress["stickers"] == ["first_walk"]


def test_completing_a_challenge_without_a_photo_is_rejected():
    client = Client()
    walk_id = _post_json(client, "/api/walks", {"user_id": "user-1", "mood": "calm", "challenges_count": 5}).json()["id"]
    walk = client.get(f"/api/walks/{walk_id}").json()
    challenge = next(c for c in walk["challenges"] if c["accepts_photo"])

    response = client.post(f"/api/walks/{walk_id}/challenges/{challenge['id']}/complete")

    assert response.status_code == 422


def test_a_third_swap_is_refused():
    client = Client()
    walk_id = _post_json(client, "/api/walks", {"user_id": "user-1", "mood": "calm", "challenges_count": 1}).json()["id"]

    for _ in range(2):
        challenge_id = client.get(f"/api/walks/{walk_id}").json()["challenges"][0]["id"]
        assert client.post(f"/api/walks/{walk_id}/challenges/{challenge_id}/swap").status_code == 204

    challenge_id = client.get(f"/api/walks/{walk_id}").json()["challenges"][0]["id"]
    assert client.post(f"/api/walks/{walk_id}/challenges/{challenge_id}/swap").status_code == 409


def test_an_unknown_walk_returns_404():
    response = Client().get(f"/api/walks/{uuid4()}")

    assert response.status_code == 404


def test_warm_up_answers_with_no_content():
    assert Client().post("/api/warmup").status_code == 204


def test_a_walk_keeps_what_the_person_wrote():
    client = Client()

    created = _post_json(client, "/api/walks", {"user_id": "user-1", "mood": "calm", "note": "  Día largo  "})

    walk = client.get(f"/api/walks/{created.json()['id']}").json()
    assert walk["note"] == "Día largo"


def test_a_walk_remembers_its_language_and_defaults_to_spanish():
    client = Client()

    english = _post_json(client, "/api/walks", {"user_id": "user-1", "mood": "calm", "language": "en"})
    default = _post_json(client, "/api/walks", {"user_id": "user-1", "mood": "calm"})

    assert client.get(f"/api/walks/{english.json()['id']}").json()["language"] == "en"
    assert client.get(f"/api/walks/{default.json()['id']}").json()["language"] == "es"


def test_a_challenge_can_be_completed_with_a_story():
    client = Client()
    walk_id = _post_json(client, "/api/walks", {"user_id": "user-1", "mood": "calm", "challenges_count": 1}).json()["id"]
    challenge = client.get(f"/api/walks/{walk_id}").json()["challenges"][0]

    completed = client.post(
        f"/api/walks/{walk_id}/challenges/{challenge['id']}/complete", {"story": "Un banco de madera con musgo."}
    )

    assert completed.status_code == 204
    saved = client.get(f"/api/walks/{walk_id}").json()["challenges"][0]
    assert (saved["status"], saved["story"]) == ("completed", "Un banco de madera con musgo.")


def test_transcribing_without_a_configured_service_answers_503(settings):
    settings.ELEVENLABS_API_KEY = ""
    voice = SimpleUploadedFile("voice.webm", b"audio", content_type="audio/webm")

    response = Client().post("/api/transcribe", {"audio": voice})

    assert response.status_code == 503


def test_transcribing_returns_the_text(monkeypatch):
    from tests.microadventures.application.test_transcribe_audio import StubSpeechTranscriber

    monkeypatch.setattr(wiring, "_speech_transcriber", lambda: StubSpeechTranscriber("Se oye una fuente."))
    voice = SimpleUploadedFile("voice.webm", b"audio", content_type="audio/webm")

    response = Client().post("/api/transcribe", {"audio": voice})

    assert response.json() == {"text": "Se oye una fuente."}


def test_the_walk_says_who_wrote_each_challenge():
    client = Client()
    created = _post_json(client, "/api/walks", {"user_id": "user-1", "mood": "calm", "challenges_count": 2})

    walk = client.get(f"/api/walks/{created.json()['id']}").json()

    assert [c["source"] for c in walk["challenges"]] == ["template", "template"]  # the test setup uses the templates
