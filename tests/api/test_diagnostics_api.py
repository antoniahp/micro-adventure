from django.test import Client

from api import wiring
from tests.microadventures.infrastructure.test_ollama_diagnostics import Http, Reply


def test_the_ollama_check_needs_the_key(settings):
    settings.REMINDERS_KEY = "secret"

    assert Client().get("/api/diagnostics/ollama?key=wrong").status_code == 403


def test_the_ollama_check_reports_text_and_vision(settings, monkeypatch):
    settings.REMINDERS_KEY = "secret"
    settings.OLLAMA_MODEL = settings.OLLAMA_VISION_MODEL = "m"
    monkeypatch.setattr(wiring, "_ollama_http", lambda: Http({"m": Reply(200, {"response": "ok"})}))

    body = Client().get("/api/diagnostics/ollama?key=secret").json()

    assert body["text"]["ok"] and body["vision"]["ok"]
