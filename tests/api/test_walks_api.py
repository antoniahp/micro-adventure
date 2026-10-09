import json
from uuid import uuid4

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client

from api import wiring
from tests.fakes import InMemoryWalkRepository
from microadventures.infrastructure.template_challenge_generator import CHALLENGE_TEXTS_EN, TemplateChallengeGenerator


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

    created = _post_json(client, "/api/walks", {"user_id": "user-1", "mood": "calm"})
    assert created.status_code == 201
    walk_id = created.json()["id"]

    walk = client.get(f"/api/walks/{walk_id}").json()
    assert len(walk["challenges"]) == 3
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
    walk_id = _post_json(client, "/api/walks", {"user_id": "user-1", "mood": "calm", "minutes": 45}).json()["id"]
    walk = client.get(f"/api/walks/{walk_id}").json()
    challenge = next(c for c in walk["challenges"] if c["accepts_photo"])

    response = client.post(f"/api/walks/{walk_id}/challenges/{challenge['id']}/complete")

    assert response.status_code == 422


def test_a_third_swap_is_refused():
    client = Client()
    walk_id = _post_json(client, "/api/walks", {"user_id": "user-1", "mood": "calm"}).json()["id"]

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
    walk_id = _post_json(client, "/api/walks", {"user_id": "user-1", "mood": "calm"}).json()["id"]
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
    created = _post_json(client, "/api/walks", {"user_id": "user-1", "mood": "calm"})

    walk = client.get(f"/api/walks/{created.json()['id']}").json()

    assert [c["source"] for c in walk["challenges"]] == ["template"] * 3  # the test setup uses the templates


def test_a_walk_has_the_usual_number_of_challenges_for_its_time():
    client = Client()

    def count_for(body):
        created = _post_json(client, "/api/walks", {"user_id": "user-1", "mood": "calm", **body})
        return len(client.get(f"/api/walks/{created.json()['id']}").json()["challenges"])

    assert count_for({"minutes": 30}) == 3
    assert count_for({"minutes": 45}) == 5
    assert count_for({"minutes": 60}) == 6
    assert count_for({"minutes": 90, "challenges_count": 10}) == 10


def test_a_number_of_challenges_that_does_not_fit_the_time_is_refused():
    response = _post_json(Client(), "/api/walks", {"user_id": "user-1", "mood": "tired", "minutes": 30, "challenges_count": 8})

    assert response.status_code == 422


def test_a_walk_can_be_finished_with_time_distance_and_a_story():
    client = Client()
    walk_id = _post_json(client, "/api/walks", {"user_id": "user-1", "mood": "calm"}).json()["id"]

    finished = _post_json(
        client,
        f"/api/walks/{walk_id}/finish",
        {"walked_minutes": 42, "distance_km": 3.4, "diary": "  Salí cansada y volví con la cabeza más limpia.  "},
    )

    assert finished.status_code == 204
    walk = client.get(f"/api/walks/{walk_id}").json()
    assert (walk["walked_minutes"], walk["distance_km"]) == (42, 3.4)
    assert walk["diary"] == "Salí cansada y volví con la cabeza más limpia."
    assert walk["finished_at"] is not None


def test_time_distance_and_story_are_optional_when_finishing():
    client = Client()
    walk_id = _post_json(client, "/api/walks", {"user_id": "user-1", "mood": "calm"}).json()["id"]

    assert _post_json(client, f"/api/walks/{walk_id}/finish", {}).status_code == 204

    walk = client.get(f"/api/walks/{walk_id}").json()
    assert (walk["walked_minutes"], walk["distance_km"], walk["diary"]) == (None, None, "")
    assert walk["finished_at"] is not None


def test_a_walk_that_is_not_finished_has_no_finish_data():
    client = Client()
    walk_id = _post_json(client, "/api/walks", {"user_id": "user-1", "mood": "calm"}).json()["id"]

    walk = client.get(f"/api/walks/{walk_id}").json()

    assert (walk["walked_minutes"], walk["distance_km"], walk["diary"], walk["finished_at"]) == (None, None, "", None)


def test_finishing_with_impossible_numbers_is_refused():
    client = Client()
    walk_id = _post_json(client, "/api/walks", {"user_id": "user-1", "mood": "calm"}).json()["id"]

    assert _post_json(client, f"/api/walks/{walk_id}/finish", {"distance_km": -1}).status_code == 422
    assert _post_json(client, f"/api/walks/{walk_id}/finish", {"walked_minutes": 0}).status_code == 422


def test_finishing_an_unknown_walk_returns_404():
    assert _post_json(Client(), f"/api/walks/{uuid4()}/finish", {}).status_code == 404


def test_a_swap_can_ask_for_the_language_on_screen():
    client = Client()
    created = _post_json(client, "/api/walks", {"user_id": "user-1", "mood": "calm", "language": "es"})
    walk_id = created.json()["id"]
    challenge_id = client.get(f"/api/walks/{walk_id}").json()["challenges"][0]["id"]

    swapped = client.post(f"/api/walks/{walk_id}/challenges/{challenge_id}/swap?language=en")

    assert swapped.status_code == 204
    new_text = client.get(f"/api/walks/{walk_id}").json()["challenges"][0]["text"]
    english_texts = {text for texts in CHALLENGE_TEXTS_EN.values() for text in texts}
    assert new_text in english_texts
