import json

import pytest

from microadventures.domain.exceptions.photo_verification_failed_exception import PhotoVerificationFailedException
from microadventures.infrastructure.api.ollama_photo_verifier import OllamaPhotoVerifier
from tests.microadventures.object_mothers import a_challenge


class FakeHttp:
    def __init__(self, body):
        self.body, self.sent = body, None

    def post(self, url, json=None, timeout=None):
        self.sent = json
        return self

    def raise_for_status(self):
        pass

    def json(self):
        return self.body


def verify(answer, **extra):
    http = FakeHttp({"response": answer, **extra})
    return OllamaPhotoVerifier("http://x", "m", http=http).verify(a_challenge(), b"photo"), http


def test_a_photo_that_does_not_match_is_rejected_with_the_reason():
    verdict, _ = verify("RECHAZADA: se ve un teclado, no un árbol")

    assert not verdict.accepted and "teclado" in verdict.reason


def test_a_photo_that_matches_is_accepted():
    assert verify("ACEPTADA: un roble grande")[0].accepted


def test_the_json_form_is_still_understood_and_a_textual_false_is_a_rejection():
    assert not verify(json.dumps({"accepted": "false", "reason": "no"}))[0].accepted
    assert verify(json.dumps({"accepted": True}))[0].accepted


def test_it_asks_for_a_short_answer_without_thinking_or_json_mode():
    _, http = verify("ACEPTADA")

    assert http.sent["think"] is False and "format" not in http.sent


def test_an_answer_that_ends_up_in_the_thinking_field_is_still_read():
    assert not verify("", thinking="RECHAZADA: una pantalla")[0].accepted


@pytest.mark.parametrize("answer", ["", "no puedo ayudar con eso"])
def test_an_empty_or_unreadable_answer_is_a_verification_failure(answer):
    with pytest.raises(PhotoVerificationFailedException):
        verify(answer)
