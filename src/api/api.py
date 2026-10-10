from django.conf import settings
from ninja import File, NinjaAPI, Schema, Status
from ninja.files import UploadedFile

from api import wiring
from api.account.account_view import router as account_router
from api.auth.auth_view import router as auth_router
from api.auth.session import UserAuth
from api.context.context_view import router as context_router
from api.diagnostics.diagnostics_view import router as diagnostics_router
from api.errors import register_error_handlers
from api.progress.progress_view import router as progress_router
from api.reminders.reminders_view import clock_router, router as reminders_router
from api.telegram.telegram_view import router as telegram_router, user_router as telegram_user_router
from api.summary.summary_view import router as summary_router
from api.walks.walks_view import router as walks_router
from microadventures.application.commands.warm_up_generator.warm_up_generator_command import WarmUpGeneratorCommand
from microadventures.application.queries.transcribe_audio.transcribe_audio_query import TranscribeAudioQuery

# Private by default: every route asks for a token unless it says auth=None (health, the session start,
# the Telegram webhook and the keyed clock/diagnostics). The API documentation only exists in development.
api = NinjaAPI(
    title="MicroAdventures API",
    urls_namespace="walks_api",
    auth=UserAuth,
    docs_url="/docs" if settings.DEBUG else None,
    openapi_url="/openapi.json" if settings.DEBUG else None,
)
api.add_router("/auth", auth_router)
api.add_router("/users", account_router)
api.add_router("/walks", walks_router)
api.add_router("/context", context_router)
api.add_router("/users", progress_router)
api.add_router("/users", summary_router)
api.add_router("/users", reminders_router)
api.add_router("/users", telegram_user_router)
api.add_router("/telegram", telegram_router, auth=None)
api.add_router("/reminders", clock_router, auth=None)
api.add_router("/diagnostics", diagnostics_router, auth=None)
register_error_handlers(api)


@api.get("/health", response={200: None}, auth=None)
def health(request):
    return Status(200, None)


@api.post("/warmup", response={204: None})
def warm_up(request):
    """The web client calls this when the form opens, so the model is loaded by the time it is submitted."""
    wiring.warm_up_generator_handler().handle(WarmUpGeneratorCommand())
    return Status(204, None)


class TranscriptionOut(Schema):
    text: str


@api.post("/transcribe", response=TranscriptionOut)
def transcribe(request, audio: UploadedFile = File(...)):
    """Turns a voice note into text. The client shows the text so the person can fix it before sending."""
    text = wiring.transcribe_audio_handler().handle(
        TranscribeAudioQuery(audio=audio.read(), content_type=audio.content_type or "audio/webm")
    )
    return {"text": text}
