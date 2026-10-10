import requests

from microadventures.infrastructure.api.ollama_diagnostics import check_ollama


class Reply:
    def __init__(self, status, body=None, text=""):
        self.status_code, self.body, self.text = status, body or {}, text

    def raise_for_status(self):
        if self.status_code >= 400:
            raise requests.HTTPError(f"{self.status_code} Client Error", response=self)

    def json(self):
        return self.body


class Http:
    def __init__(self, by_model):
        self.by_model, self.sent = by_model, []

    def post(self, url, json=None, timeout=None):
        self.sent.append(json)
        return self.by_model[json["model"]]


def check(http, **kwargs):
    return check_ollama(http, "https://ollama.com", "text-model", "vision-model", 30, has_api_key=True, **kwargs)


def test_it_reports_which_model_works_and_which_does_not():
    http = Http({"text-model": Reply(200, {"response": "hello"}), "vision-model": Reply(404, text='{"error":"model not found"}')})

    report = check(http)

    assert report["text"]["ok"] and report["text"]["answer"] == "hello"
    assert not report["vision"]["ok"] and report["vision"]["status"] == 404
    assert "model not found" in report["vision"]["error"]


def test_the_vision_call_sends_a_real_image_and_the_report_never_has_the_key():
    http = Http({"text-model": Reply(200, {"response": "x"}), "vision-model": Reply(200, {"response": "green"})})

    report = check(http)

    assert http.sent[1]["images"][0].startswith("iVBORw0KGgo")  # a PNG
    assert report["config"]["api_key_set"] is True
    assert "Bearer" not in str(report)
