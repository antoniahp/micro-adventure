import os
from datetime import timedelta
from pathlib import Path

import sentry_sdk

from core.sentry_scrubber import before_send, before_send_log

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ["DJANGO_SECRET_KEY"]
# The admin lives at /<ADMIN_URL>/. A path only you know keeps bots from trying passwords on /admin/.
ADMIN_URL = os.environ.get("ADMIN_URL", "admin").strip("/")
DEBUG = os.environ.get("DEBUG", "False").lower() in ["true", "1", "yes"]
# "*" only as a local-development fallback; Render needs its own value set, e.g. micro-adventure.onrender.com.
ALLOWED_HOSTS = os.environ.get("ALLOWED_HOSTS", "*").split(",")
# Optional: the OAuth client id from Google Cloud Console. Empty means "Sign in with Google" stays off —
# the button still shows, but linking fails with a clear error instead of a broken script.
GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID", "")

INSTALLED_APPS = [
    # Django admin and its dependencies, with MongoDB-ready AppConfigs (see core/apps.py).
    "core.apps.MongoAdminConfig",
    "core.apps.MongoAuthConfig",
    "core.apps.MongoContentTypesConfig",
    "django.contrib.messages",
    "django.contrib.sessions",
    "django.contrib.staticfiles",
    "microadventures",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",  # blocks the app being framed by another site
    "core.middleware.ContentSecurityPolicyMiddleware",  # tells the browser which sources of script/style/etc. to trust
    "core.middleware.MaxBodySizeMiddleware",  # refuses an oversized body before Django reads any of it
    "core.middleware.RateLimitMiddleware",  # caps requests per IP, tighter on the routes that call Gemma/ElevenLabs
    "whitenoise.middleware.WhiteNoiseMiddleware",  # serves the admin CSS in production
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
]

# A multipart body (a photo) past this size is refused outright; the client already shrinks photos well under it.
MAX_BODY_BYTES = 8 * 1024 * 1024

# (requests allowed, over this many seconds) per kind of route. The model routes cost money and a slow
# reply each, so they get a tighter budget than a simple read. Off in tests by default (see tests/conftest.py).
RATE_LIMIT_ENABLED = True
RATE_LIMITS = {"model": (12, 60), "default": (120, 60)}

ROOT_URLCONF = "core.urls"
WSGI_APPLICATION = "core.wsgi.application"

# Used by the admin and by django-ninja's Swagger page at /api/docs.
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ]
        },
    }
]

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

# In production one service serves everything: the Django API and the built web client.
# The Dockerfile.render image puts the client in web_dist/; whitenoise serves it at "/".
# In local development the folder does not exist and Vite serves the client instead.
WEB_DIST = BASE_DIR.parent / "web_dist"
if WEB_DIST.is_dir():
    WHITENOISE_ROOT = WEB_DIST
    WHITENOISE_INDEX_FILE = True

# Behind Render's HTTPS proxy: trust its header, and accept the service's own address for admin logins.
if not DEBUG:
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    # Tells browsers that have already visited to always use HTTPS here, even if someone types http://.
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
X_FRAME_OPTIONS = "DENY"  # nobody can put the app inside an <iframe> on another site (clickjacking)

# What the browser is allowed to load, for both faces of this app (the React client and the Django admin).
# style-src needs 'unsafe-inline': React sets style={{...}} directly, all over the web client.
# script-src/style-src/connect-src/frame-src allow accounts.google.com: it's the optional "Sign in with
# Google" button (Google's own script and the stylesheet it injects for that button) — nothing else is
# added for it.
CONTENT_SECURITY_POLICY = (
    "default-src 'self'; "
    "script-src 'self' https://accounts.google.com; "
    "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com https://accounts.google.com; "
    "font-src 'self' https://fonts.gstatic.com; "
    "img-src 'self' data: blob:; "
    "connect-src 'self' https://accounts.google.com; "
    "frame-src https://accounts.google.com; "
    "object-src 'none'; "
    "base-uri 'self'; "
    "form-action 'self'; "
    "frame-ancestors 'none'"
)
CSRF_TRUSTED_ORIGINS = [
    origin for origin in [os.environ.get("RENDER_EXTERNAL_URL", ""), *os.environ.get("CSRF_TRUSTED_ORIGINS", "").split(",")] if origin
]

# MongoDB Atlas, through the official django-mongodb-backend.
# In production MONGODB_URI is the Atlas connection string (mongodb+srv://...).
DATABASES = {
    "default": {
        "ENGINE": "django_mongodb_backend",
        "HOST": os.environ.get("MONGODB_URI", "mongodb://localhost:27017"),
        "NAME": os.environ.get("MONGODB_DB", "micro_adventure"),
    }
}

# Keeps embedded models (Challenge) from getting a collection of their own.
DATABASE_ROUTERS = ["django_mongodb_backend.routers.MongoRouter"]

DEFAULT_AUTO_FIELD = "django_mongodb_backend.fields.ObjectIdAutoField"

# The contrib apps need migrations written for MongoDB (generated once, see mongo_migrations/).
MIGRATION_MODULES = {
    "admin": "mongo_migrations.admin",
    "auth": "mongo_migrations.auth",
    "contenttypes": "mongo_migrations.contenttypes",
}
USE_TZ = True

# Open model served by Ollama. Check the exact tag with `ollama list`.
OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://localhost:11434")
OLLAMA_API_KEY = os.environ.get("OLLAMA_API_KEY", "")  # for a hosted Ollama behind a proxy that asks for it
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "gemma3:latest")
OLLAMA_VISION_MODEL = os.environ.get("OLLAMA_VISION_MODEL", OLLAMA_MODEL)
OLLAMA_TIMEOUT_SECONDS = float(os.environ.get("OLLAMA_TIMEOUT_SECONDS", "30"))

# Voice notes are transcribed with ElevenLabs. Without a key, people can still write their story.
ELEVENLABS_API_KEY = os.environ.get("ELEVENLABS_API_KEY", "")
ELEVENLABS_STT_MODEL = os.environ.get("ELEVENLABS_STT_MODEL", "scribe_v2")

# "ollama" checks photos with the vision model. "trusting" accepts every photo (plan B).
PHOTO_VERIFIER = os.environ.get("PHOTO_VERIFIER", "ollama")

if dsn := os.environ.get("SENTRY_DSN"):
    # Every request is traced (this is a small app), so the model calls show up with their latency and tokens.
    sentry_sdk.init(
        dsn=dsn,
        environment=os.environ.get("SENTRY_ENVIRONMENT", "development"),
        traces_sample_rate=1.0,
        send_default_pii=False,
        before_send=before_send,
        before_send_transaction=before_send,  # the Telegram URL (with the bot token) shows up in spans
        enable_logs=True,  # Python logging (warnings and errors) also goes to Sentry Logs
        before_send_log=before_send_log,
    )

# The app's own messages (INFO and up) go to the console and, with enable_logs, to Sentry Logs.
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "filters": {"secrets": {"()": "core.sentry_scrubber.SecretsFilter"}},  # no key reaches the Render logs
    "handlers": {"console": {"class": "logging.StreamHandler", "filters": ["secrets"]}},
    "loggers": {"microadventures": {"handlers": ["console"], "level": "INFO"}},
}

# --- Sessions ---
# Every browser gets an anonymous account and signed tokens (django-ninja-jwt), signed with SECRET_KEY.
# The short access token goes in each request; the refresh token, kept by the browser, gets a new pair.
# A year, not 30 days: the refresh is renewed on every visit, so only someone away from the app a full year
# (not just away from walking) would need a new, empty session.
NINJA_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=30),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=365),
}

# --- Reminders by Telegram ---
# The bot is made with @BotFather. Without a token the app works and just cannot send reminders.
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_BOT_USERNAME = os.environ.get("TELEGRAM_BOT_USERNAME", "").lstrip("@")
# An outside clock (cron-job.org) calls /api/reminders/run?key=... every few minutes. Empty = those calls are refused.
REMINDERS_KEY = os.environ.get("REMINDERS_KEY", "")
# Where the reminder sends people. Render fills RENDER_EXTERNAL_URL itself.
APP_URL = os.environ.get("APP_URL") or os.environ.get("RENDER_EXTERNAL_URL", "")
