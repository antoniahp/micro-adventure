import json
import random

import pytest

from tests.fakes import StubChallengeGenerator
from tests.microadventures.object_mothers import a_challenge
from microadventures.domain.models.challenge_brief import ChallengeBrief
from microadventures.domain.models.challenge_category import ChallengeCategory
from microadventures.domain.exceptions.challenge_generation_failed_exception import ChallengeGenerationFailedException
from microadventures.domain.models.language import Language
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


@pytest.mark.parametrize("output", ["not json", '{"challenges": []}', '{"challenges": [{"category": "sound", "text": ""}]}'])
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


def test_ollama_prompt_asks_for_english_when_the_walk_is_in_english():
    http = FakeHttp(json.dumps({"challenges": [{"category": "nature", "text": "Look at a tree."}]}))
    brief = ChallengeBrief(mood=Mood.CALM, minutes=30, weather="clear", count=1, note="Long day", language=Language.EN)

    OllamaChallengeGenerator("http://ollama", "gemma", http=http).generate(brief)

    prompt = http.requests[0][1]["prompt"]
    assert "written in English" in prompt and "Long day" in prompt


def test_template_generator_writes_in_the_requested_language():
    from microadventures.infrastructure.template_challenge_generator import CHALLENGE_TEXTS_EN

    brief = ChallengeBrief(mood=Mood.CALM, minutes=30, weather="clear", count=5, language=Language.EN)

    challenges = TemplateChallengeGenerator().generate(brief)

    assert all(c.text in CHALLENGE_TEXTS_EN[c.category] for c in challenges)


def _ollama_answering(items):
    http = FakeHttp(json.dumps({"challenges": items}))
    return OllamaChallengeGenerator("http://ollama", "gemma", http=http)


def test_ollama_accepts_the_category_written_the_way_models_write_it():
    items = [{"category": "Touch", "text": "Toca una hoja."}, {"category": "TACTO", "text": "Toca musgo."}]
    brief = ChallengeBrief(mood=Mood.CALM, minutes=30, weather="clear", count=2)

    challenges = _ollama_answering(items).generate(brief)

    assert [c.category for c in challenges] == [ChallengeCategory.SENSORY, ChallengeCategory.SENSORY]


def test_ollama_does_not_fail_on_an_unknown_category_word():
    brief = ChallengeBrief(mood=Mood.CALM, minutes=30, weather="clear", count=1)

    challenges = _ollama_answering([{"category": "relax", "text": "Respira hondo."}]).generate(brief)

    assert challenges[0].text == "Respira hondo."


def test_ollama_forces_the_category_of_a_swap():
    brief = ChallengeBrief(mood=Mood.CALM, minutes=30, weather="clear", count=1, category=ChallengeCategory.SOUND)

    challenges = _ollama_answering([{"category": "nature", "text": "Escucha el viento."}]).generate(brief)

    assert challenges[0].category == ChallengeCategory.SOUND


def test_ollama_accepts_a_bare_list_or_another_key():
    brief = ChallengeBrief(mood=Mood.CALM, minutes=30, weather="clear", count=2)
    items = [{"category": "sound", "text": "Escucha el viento."}, {"category": "nature", "reto": "Mira un árbol."}]

    wrapped_with_other_key = OllamaChallengeGenerator("http://ollama", "gemma", http=FakeHttp(json.dumps({"retos": items})))
    bare_list = OllamaChallengeGenerator("http://ollama", "gemma", http=FakeHttp(json.dumps(items)))

    assert [c.text for c in wrapped_with_other_key.generate(brief)] == ["Escucha el viento.", "Mira un árbol."]
    assert [c.text for c in bare_list.generate(brief)] == ["Escucha el viento.", "Mira un árbol."]


def test_ollama_asks_for_a_different_category_per_challenge_in_a_random_order():
    answer = json.dumps({"challenges": [{"category": "sound", "text": "a"}] * 3})
    orders = set()
    for seed in range(8):
        http = FakeHttp(answer)
        brief = ChallengeBrief(mood=Mood.CALM, minutes=30, weather="clear", count=3)
        OllamaChallengeGenerator("http://ollama", "gemma", http=http, rng=random.Random(seed)).generate(brief)
        prompt = http.requests[0][1]["prompt"]
        order = prompt.split("en este orden: ")[1].split(".")[0].split(", ")
        assert len(set(order)) == 3  # no repeated category within a walk
        orders.add(tuple(order))
    assert len(orders) > 1  # and walks do not all start the same way
