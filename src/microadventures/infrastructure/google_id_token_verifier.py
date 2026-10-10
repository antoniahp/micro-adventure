from django.conf import settings
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token as google_id_token

from microadventures.domain.exceptions.invalid_google_token_exception import InvalidGoogleTokenException
from microadventures.domain.services.google_identity_verifier import GoogleIdentityVerifier

_request = google_requests.Request()  # one HTTP transport, reused so Google's signing keys get cached


class GoogleIdTokenVerifier(GoogleIdentityVerifier):
    def verify(self, id_token: str) -> tuple[str, str]:
        if not settings.GOOGLE_CLIENT_ID:
            raise InvalidGoogleTokenException()
        try:
            claims = google_id_token.verify_oauth2_token(id_token, _request, settings.GOOGLE_CLIENT_ID)
        except ValueError:
            raise InvalidGoogleTokenException()
        sub = claims.get("sub")
        email = claims.get("email")
        if not sub or not email or not claims.get("email_verified"):
            raise InvalidGoogleTokenException()
        return sub, email
