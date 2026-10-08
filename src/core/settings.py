import os
from pathlib import Path

import sentry_sdk

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ["DJANGO_SECRET_KEY"]
DEBUG = os.environ.get("DEBUG", "False").lower() in ["true", "1", "yes"]
ALLOWED_HOSTS = os.environ.get("ALLOWED_HOSTS", "*").split(",")

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
    "whitenoise.middleware.WhiteNoiseMiddleware",  # serves the admin CSS in production
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
]

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
    )
