from core.sentry_scrubber import FILTERED, before_send, scrub


def test_the_bot_token_never_reaches_sentry():
    event = {"spans": [{"description": "POST https://api.telegram.org/bot123456:ABC-def_GHI/sendMessage"}]}

    cleaned = before_send(event, {})

    assert cleaned["spans"][0]["description"] == "POST https://api.telegram.org/bot123456:[Filtered]/sendMessage"


def test_the_reminders_key_is_hidden_in_urls():
    event = {"request": {"url": "https://x.onrender.com/api/reminders/run?key=secret-1&other=1"}}

    assert before_send(event, {})["request"]["url"] == "https://x.onrender.com/api/reminders/run?key=[Filtered]&other=1"


def test_events_without_secrets_stay_the_same():
    event = {"message": "hello", "tags": [("a", 1)]}

    assert before_send(event, {}) == event


def test_logs_are_scrubbed_too():
    from core.sentry_scrubber import before_send_log

    log = {"body": "POST https://api.telegram.org/bot123:abc-DEF/sendMessage failed", "attributes": {}}
    assert "abc-DEF" not in before_send_log(log, {})["body"]


def test_any_secret_in_the_environment_is_hidden_wherever_it_appears(monkeypatch):
    monkeypatch.setenv("ELEVENLABS_API_KEY", "el-super-secret-123")
    event = {"message": "failed with el-super-secret-123 in the middle"}

    assert "el-super-secret-123" not in before_send(event, {})["message"]


def test_the_mongodb_user_and_password_are_hidden():
    from core.sentry_scrubber import scrub_text

    text = "ServerSelectionTimeout mongodb+srv://anto:p4ss@cluster0.abc.mongodb.net/db"
    assert scrub_text(text) == "ServerSelectionTimeout mongodb+srv://[Filtered]@cluster0.abc.mongodb.net/db"


def test_authorization_headers_and_sensitive_fields_are_hidden():
    event = {"request": {"headers": {"Authorization": "Bearer abc.def", "Accept": "json"}, "data": {"api_key": "k1"}}}

    cleaned = before_send(event, {})["request"]
    assert cleaned["headers"] == {"Authorization": "[Filtered]", "Accept": "json"}
    assert cleaned["data"] == {"api_key": "[Filtered]"}


def test_console_logs_are_scrubbed(caplog):
    import logging

    from core.sentry_scrubber import SecretsFilter

    record = logging.LogRecord("microadventures", logging.WARNING, "x", 1, "call %s failed", ("https://a/run?key=abc123",), None)
    SecretsFilter().filter(record)
    assert record.getMessage() == "call https://a/run?key=[Filtered] failed"


def test_the_gunicorn_access_log_hides_the_key():
    import logging

    from core.gunicorn_logging import RedactingLogger
    from core.sentry_scrubber import SecretsFilter

    record = logging.LogRecord("gunicorn.access", logging.INFO, "x", 1, '"GET %(p)s"', ({"p": "/run?key=abc"},), None)
    SecretsFilter().filter(record)
    assert record.getMessage() == '"GET /run?key=[Filtered]"' and RedactingLogger


def test_token_counts_reach_sentry_while_tokens_stay_out():
    # The span data of a model call: the counts are what Sentry's AI views are built on, not secrets.
    span_data = {
        "gen_ai.usage.input_tokens": 430,
        "gen_ai.usage.output_tokens": 21,
        "gen_ai.usage.total_tokens": 451,
        "gen_ai.response.tokens_per_second": 24.5,
        "access_token": "eyJhbGciOi.secret",
        "refresh_token": "eyJhbGciOi.other",
        "bot_token": "123456:ABC-secret",
    }

    scrubbed = scrub(span_data)

    assert scrubbed["gen_ai.usage.input_tokens"] == 430
    assert scrubbed["gen_ai.usage.output_tokens"] == 21
    assert scrubbed["gen_ai.usage.total_tokens"] == 451
    assert scrubbed["gen_ai.response.tokens_per_second"] == 24.5
    assert scrubbed["access_token"] == FILTERED
    assert scrubbed["refresh_token"] == FILTERED
    assert scrubbed["bot_token"] == FILTERED
