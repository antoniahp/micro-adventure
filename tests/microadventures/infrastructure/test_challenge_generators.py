import json
import random

import pytest

from tests.fakes import StubChallengeGenerator
from tests.microadventures.object_mothers import a_challenge
from microadventures.domain.models.challenge_brief import ChallengeBrief
from microadventures.domain.models.challenge_category import ChallengeCategory
from microadventures.domain.exceptions.challenge_generation_failed_exception import ChallengeGenerationFailedException
from microadventures.domain.models.mood import Mood
from microadventures.infrastructure.fallback_challenge_generator import FallbackChallengeGenerator
from microadventures.infrastructure.api.ollama_challenge_generator import OllamaChallengeGenerator
from microadventures.infrastructure.template_challenge_generator import TemplateChallengeGenerator

BRIEF = ChallengeBrief(mood=Mood.CALM, minutes=30, weather="clear", count=2)


class FakeHttp:
    def __init__(self, model_output: str):
        self.model_output = model_output
        self.requests = []

    def post(self, url, json, timeout):
        self.requests.append((url, json))
        return self

    def raise_for_status(self):
        pass

    def json(self):
        return {"response": self.model_output}


class BrokenGenerator:
    def generate(self, brief):
        raise RuntimeError("model is down")


def test_ollama_generator_parses_the_model_output():
    output = json.dumps(
        {
            "challenges": [
                {"category": "sound", "text": "Escucha un pájaro."},
                {"category": "nature", "text": "Busca un árbol viejo."},
            ]
        }
    )
    http = FakeHttp(output)

    challenges = OllamaChallengeGenerator("http://ollama:11434/", "gemma", http=http).generate(BRIEF)

    assert [c.category for c in challenges] == [ChallengeCategory.SOUND, ChallengeCategory.NATURE]
    assert http.requests[0][0] == "http://ollama:11434/api/generate"
    assert http.requests[0][1]["model"] == "gemma"


@pytest.mark.parametrize("output", ["not json", '{"challenges": []}', '{"challenges": [{"category": "x", "text": "a"}]}'])
def test_ollama_generator_fails_on_unusable_output(output):
    with pytest.raises(ChallengeGenerationFailedException):
        OllamaChallengeGenerator("http://ollama:11434", "gemma", http=FakeHttp(output)).generate(BRIEF)


def test_template_generator_returns_the_requested_count_and_category():
    brief = ChallengeBrief(mood=Mood.TIRED, minutes=15, weather="rain", count=3, category=ChallengeCategory.SOUND)

    challenges = TemplateChallengeGenerator(random.Random(1)).generate(brief)

    assert len(challenges) == 3
    assert {c.category for c in challenges} == {ChallengeCategory.SOUND}


def test_fallback_generator_uses_the_fallback_when_the_primary_fails():
    expected = [a_challenge()]

    result = FallbackChallengeGenerator(BrokenGenerator(), StubChallengeGenerator(expected)).generate(BRIEF)

    assert result == expected


def test_ollama_prompt_includes_what_the_person_wrote():
    http = FakeHttp(json.dumps({"challenges": [{"category": "nature", "text": "Mira un árbol."}]}))
    brief = ChallengeBrief(mood=Mood.CALM, minutes=30, weather="clear", count=1, note="Vengo de una reunión eterna")

    OllamaChallengeGenerator("http://ollama", "gemma", http=http).generate(brief)

    assert "Vengo de una reunión eterna" in http.requests[0][1]["prompt"]


def test_ollama_warm_up_only_loads_the_model():
    http = FakeHttp("")

    OllamaChallengeGenerator("http://ollama", "gemma", http=http).warm_up()

    url, body = http.requests[0]
    assert url == "http://ollama/api/generate"
    assert body == {"model": "gemma", "keep_alive": "30m"}


def test_fallback_warm_up_never_fails_when_the_model_is_down():
    class DownGenerator(StubChallengeGenerator):
        def warm_up(self):
            raise RuntimeError("model is down")

    FallbackChallengeGenerator(DownGenerator([]), TemplateChallengeGenerator()).warm_up()
