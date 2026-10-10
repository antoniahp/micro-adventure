"""Two small, dependency-free guards that sit in front of every request.

No Redis here: the app runs as a single gunicorn worker (see Dockerfile.render), so Django's in-memory
cache is enough to count requests, and it resets if the process restarts - a bearable trade for a tool
this size.
"""

import time

from django.conf import settings
from django.core.cache import cache
from django.http import JsonResponse
from ninja_jwt.exceptions import TokenError
from ninja_jwt.tokens import AccessToken


def client_ip(request) -> str:
    """Cloudflare sits in front on Render; it is the only proxy we trust for the caller's real address."""
    return request.META.get("HTTP_CF_CONNECTING_IP") or request.META.get("REMOTE_ADDR", "unknown")


def _identity(request) -> str:
    """The signed-in user when the bearer token is valid (several people can share one IP); the IP otherwise.

    This only reads the token - it does not sign the request in, so a bad or missing token never blocks the
    request here. ninja's own auth, later, is what actually requires one.
    """
    header = request.META.get("HTTP_AUTHORIZATION", "")
    if header.startswith("Bearer "):
        try:
            return f"user:{AccessToken(header[7:])['user_id']}"
        except TokenError:
            pass
    return f"ip:{client_ip(request)}"


class MaxBodySizeMiddleware:
    """Refuses an oversized body by its declared Content-Length, before Django reads or buffers any of it."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        length = request.META.get("CONTENT_LENGTH")
        if length and int(length) > settings.MAX_BODY_BYTES:
            return JsonResponse({"detail": "Request too large"}, status=413)
        return self.get_response(request)


MODEL_ROUTES = (
    ("POST", "/api/walks"),
    ("POST", "/complete"),
    ("POST", "/swap"),
    ("POST", "/api/warmup"),
    ("POST", "/api/transcribe"),
)


def _bucket(request) -> str:
    path = request.path
    if any(request.method == method and (path == route or path.endswith(route)) for method, route in MODEL_ROUTES):
        return "model"
    return "default"


class RateLimitMiddleware:
    """A fixed window per IP and per bucket. Answers 429 past the limit, with Retry-After.

    Off by default in tests (settings.RATE_LIMIT_ENABLED, see tests/conftest.py): the functional tests make
    many calls in the same second on purpose, and are not the place to also exercise the limiter.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not settings.RATE_LIMIT_ENABLED:
            return self.get_response(request)
        bucket = _bucket(request)
        limit, window = settings.RATE_LIMITS[bucket]
        slot = int(time.time() // window)
        key = f"ratelimit:{bucket}:{_identity(request)}:{slot}"
        try:
            count = cache.incr(key)
        except ValueError:
            cache.set(key, 1, timeout=window)
            count = 1
        if count > limit:
            retry_after = window - int(time.time() % window)
            response = JsonResponse({"detail": "Too many requests"}, status=429)
            response.headers["Retry-After"] = str(retry_after)
            return response
        return self.get_response(request)
