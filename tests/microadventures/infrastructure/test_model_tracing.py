import json

from microadventures.domain.models.challenge_brief import ChallengeBrief
from microadventures.domain.models.mood import Mood
from microadventures.infrastructure.api import model_tracing
from microadventures.infrastructure.api.ollama_challenge_generator import OllamaChallengeGenerator


class RecordingSpan:
    def __init__(self, name):
        self.name, self.data = name, {}

    def set_data(self, key, value):
        self.data[key] = value

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False


class OllamaWithUsage:
    """Fake http that answers like Ollama: the text plus token counts and timings."""

    def post(self, url, json, timeout):
        self.sent = json
        return self

    def raise_for_status(self):
        pass

    def json(self):
        answer = {"challenges": [{"category": "nature", "text": "Mira un árbol."}]}
        return {"response": json.dumps(answer), "prompt_eval_count": 120, "eval_count": 40, "total_duration": 2_500_000_000}


def test_a_model_call_records_tokens_and_timings_but_not_what_the_person_wrote(monkeypatch):
    spans = []
    monkeypatch.setattr(model_tracing.sentry_sdk, "start_span", lambda **kw: spans.append(RecordingSpan(kw["name"])) or spans[-1])
    brief = ChallengeBrief(mood=Mood.CALM, minutes=30, weather="clear", count=1, note="Mi jefe me ha gritado hoy")

    OllamaChallengeGenerator("http://ollama", "gemma", http=OllamaWithUsage()).generate(brief)

    span = spans[0]
    assert span.name == "generate_challenges gemma"
    assert span.data["gen_ai.request.model"] == "gemma"
    assert span.data["gen_ai.usage.input_tokens"] == 120
    assert span.data["gen_ai.usage.total_tokens"] == 160
    assert span.data["ollama.total_duration_ms"] == 2500
    assert "Mi jefe" not in json.dumps(span.data)
