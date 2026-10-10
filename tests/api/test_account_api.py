import json

import pytest

from api import wiring
from tests.auth_helpers import signed_in
from tests.fakes import FakeGoogleIdentityVerifier, InMemoryAccountRepository


@pytest.fixture(autouse=True)
def in_memory_adapters(monkeypatch):
    accounts = InMemoryAccountRepository()
    verifier = FakeGoogleIdentityVerifier()
    monkeypatch.setattr(wiring, "_account_repository", lambda: accounts)
    monkeypatch.setattr(wiring, "_google_identity_verifier", lambda: verifier)
    return accounts, verifier


def test_a_fresh_account_has_no_nickname_and_no_google():
    client = signed_in("user-1")

    response = client.get("/api/users/user-1/account")

    assert response.status_code == 200
    assert response.json() == {"nickname": None, "google_linked": False}


def test_setting_a_nickname():
    client = signed_in("user-1")

    response = client.put("/api/users/user-1/account/nickname", data=json.dumps({"nickname": "Jose"}), content_type="application/json")

    assert response.status_code == 200
    assert response.json()["nickname"] == "Jose"


def test_a_blank_nickname_is_the_same_as_removing_it():
    client = signed_in("user-1")
    client.put("/api/users/user-1/account/nickname", data=json.dumps({"nickname": "Jose"}), content_type="application/json")

    response = client.put("/api/users/user-1/account/nickname", data=json.dumps({"nickname": "   "}), content_type="application/json")

    assert response.json()["nickname"] is None


def test_a_nickname_over_the_limit_is_refused():
    client = signed_in("user-1")

    response = client.put("/api/users/user-1/account/nickname", data=json.dumps({"nickname": "x" * 51}), content_type="application/json")

    assert response.status_code == 422


def test_cannot_set_another_users_nickname():
    client = signed_in("user-1")

    response = client.put("/api/users/other-user/account/nickname", data=json.dumps({"nickname": "Jose"}), content_type="application/json")

    assert response.status_code == 403


def test_linking_a_google_account():
    client = signed_in("user-1")

    response = client.post(
        "/api/users/user-1/account/google/link", data=json.dumps({"id_token": "google-sub-1:jose@gmail.com"}), content_type="application/json"
    )

    assert response.status_code == 200
    body = response.json()
    assert body == {
        "nickname": None,
        "google_linked": True,
        "switched": False,
        "user_id": "user-1",
        "access": None,
        "refresh": None,
    }


def test_an_invalid_google_credential_is_refused():
    client = signed_in("user-1")

    response = client.post("/api/users/user-1/account/google/link", data=json.dumps({"id_token": "not-a-real-token"}), content_type="application/json")

    assert response.status_code == 401


def test_reconnecting_the_same_google_account_from_a_new_browser_restores_the_old_one():
    old_browser = signed_in("old-user")
    old_browser.post("/api/users/old-user/account/google/link", data=json.dumps({"id_token": "google-sub-1:jose@gmail.com"}), content_type="application/json")
    new_browser = signed_in("new-user")

    response = new_browser.post(
        "/api/users/new-user/account/google/link", data=json.dumps({"id_token": "google-sub-1:jose@gmail.com"}), content_type="application/json"
    )

    assert response.status_code == 200
    body = response.json()
    assert body["switched"] is True
    assert body["user_id"] == "old-user"
    assert body["access"] and body["refresh"]
    # the new browser's own account was never touched
    assert new_browser.get("/api/users/new-user/account").json()["google_linked"] is False
    # and the tokens handed back are good for the old, restored account
    restored = signed_in("old-user")
    assert restored.get("/api/users/old-user/account").json()["google_linked"] is True


def test_unlinking_google():
    client = signed_in("user-1")
    client.post("/api/users/user-1/account/google/link", data=json.dumps({"id_token": "google-sub-1:jose@gmail.com"}), content_type="application/json")

    response = client.post("/api/users/user-1/account/google/unlink")

    assert response.status_code == 200
    assert response.json() == {"nickname": None, "google_linked": False}


def test_cannot_link_google_for_another_user():
    client = signed_in("user-1")

    response = client.post(
        "/api/users/other-user/account/google/link", data=json.dumps({"id_token": "google-sub-1:jose@gmail.com"}), content_type="application/json"
    )

    assert response.status_code == 403
