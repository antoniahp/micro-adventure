from django.conf import settings
from ninja import Router

from api import wiring
from api.key_guard import check_key
from microadventures.infrastructure.api.ollama_diagnostics import check_ollama

router = Router()


@router.get("/ollama")
def ollama(request, key: str):
    """Tries the text and the vision model with the configured settings and says what went wrong. Needs the REMINDERS_KEY."""
    check_key(key)
    return check_ollama(
        http=wiring._ollama_http(),
        base_url=settings.OLLAMA_URL,
        model=settings.OLLAMA_MODEL,
        vision_model=settings.OLLAMA_VISION_MODEL,
        timeout=settings.OLLAMA_TIMEOUT_SECONDS,
        has_api_key=bool(settings.OLLAMA_API_KEY),
    )
