import json

import pytest

from microadventures.domain.exceptions.photo_verification_failed_exception import PhotoVerificationFailedException
from microadventures.infrastructure.api.ollama_photo_verifier import OllamaPhotoVerifier
from tests.microadventures.object_mothers import a_challenge


class FakeHttp:
    def __init__(self, answer):
        self.answer = answer

    def post(self, url, json=None, timeout=None):
        return self

    def raise_for_status(self):
        pass

    def json(self):
        return {"response": self.answer}


def verify(answer: str):
    return OllamaPhotoVerifier("http://x", "m", http=FakeHttp(answer)).verify(a_challenge(), b"photo")


def test_a_photo_that_does_not_match_is_rejected_with_the_reason():
    verdict = verify(json.dumps({"seen": "un teclado", "accepted": False, "reason": "No es un árbol"}))

    assert not verdict.accepted and verdict.reason == "No es un árbol"


def test_an_answer_of_false_written_as_text_is_still_a_rejection():
    assert not verify(json.dumps({"accepted": "false"})).accepted


def test_an_answer_that_is_not_json_is_a_verification_failure():
    with pytest.raises(PhotoVerificationFailedException):
        verify("no puedo ayudar")
