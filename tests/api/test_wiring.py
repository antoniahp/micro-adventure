import requests

from api import wiring


def test_without_a_key_ollama_is_called_with_plain_requests(settings):
    settings.OLLAMA_API_KEY = ""

    assert wiring._ollama_http() is requests


def test_with_a_key_every_ollama_call_carries_it(settings):
    settings.OLLAMA_API_KEY = "secret-key"

    http = wiring._ollama_http()

    assert http.headers["Authorization"] == "Bearer secret-key"


def test_the_generator_and_the_photo_verifier_use_that_key(settings):
    settings.OLLAMA_API_KEY = "secret-key"
    settings.PHOTO_VERIFIER = "ollama"

    generator = wiring._challenge_generator().primary
    verifier = wiring._photo_verifier()

    assert generator.http.headers["Authorization"] == "Bearer secret-key"
    assert verifier.http.headers["Authorization"] == "Bearer secret-key"
