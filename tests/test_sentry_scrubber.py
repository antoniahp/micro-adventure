from core.sentry_scrubber import before_send


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
