"""The redirect-flow landing page Google's "Sign in with Google" posts back to (see
core/google_redirect_view.py). The popup flow (ux_mode="popup") never reaches this view, so these
tests are the only coverage of it.
"""

from django.test import Client


def test_it_sends_the_credential_back_in_the_url_fragment_and_never_to_any_server():
    client = Client()
    client.cookies["g_csrf_token"] = "token-1"

    response = client.post("/google/redirect-login", {"credential": "the-jwt", "g_csrf_token": "token-1"})

    assert response.status_code == 302
    assert response["Location"] == "/#google_credential=the-jwt"


def test_a_mismatched_csrf_token_is_refused():
    client = Client()
    client.cookies["g_csrf_token"] = "token-1"

    response = client.post("/google/redirect-login", {"credential": "the-jwt", "g_csrf_token": "token-2"})

    assert response.status_code == 400


def test_a_missing_csrf_token_is_refused():
    client = Client()

    response = client.post("/google/redirect-login", {"credential": "the-jwt"})

    assert response.status_code == 400


def test_get_is_not_allowed():
    client = Client()

    response = client.get("/google/redirect-login")

    assert response.status_code == 405
