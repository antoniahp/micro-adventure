from django.test import Client

from api.auth.session import issue_tokens


def signed_in(user_id: str = "user-1") -> Client:
    """A test client that carries the bearer token of an anonymous user, like the web app does."""
    client = Client(HTTP_AUTHORIZATION=f"Bearer {issue_tokens(user_id)['access']}")
    client.user_id = user_id
    return client
