"""Who is asking. A bearer token (JWT) says which anonymous user it is; no database lookup is needed to read it.

`UserAuth` is the default for the whole API (see api.py): a route is private unless it says `auth=None`.
"""

from ninja.errors import HttpError
from ninja_jwt.authentication import JWTTokenUserAuth
from ninja_jwt.exceptions import TokenError
from ninja_jwt.tokens import RefreshToken

UserAuth = JWTTokenUserAuth()


def issue_tokens(user_id: str) -> dict:
    refresh = RefreshToken()
    refresh["user_id"] = user_id
    return {"user_id": user_id, "access": str(refresh.access_token), "refresh": str(refresh)}


def renew_tokens(refresh_token: str) -> dict:
    """A valid refresh token gets a new pair, so a person who keeps coming back never has to start over."""
    try:
        refresh = RefreshToken(refresh_token)
    except TokenError:
        raise HttpError(401, "Invalid or expired token")
    return issue_tokens(refresh["user_id"])


def current_user_id(request) -> str:
    return str(request.auth.id)


def ensure_own_user(request, user_id: str) -> None:
    """The user in the URL has to be the user in the token: knowing someone's id opens nothing."""
    if user_id != current_user_id(request):
        raise HttpError(403, "Forbidden")
