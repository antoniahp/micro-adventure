from ninja import File, NinjaAPI, Schema, Status
from ninja.files import UploadedFile

from api import wiring
from api.errors import register_error_handlers
from api.routers.progress import router as progress_router
from api.routers.walks import router as walks_router
from microadventures.application.commands.warm_up_generator.warm_up_generator_command import WarmUpGeneratorCommand
from microadventures.application.queries.transcribe_audio.transcribe_audio_query import TranscribeAudioQuery

api = NinjaAPI(title="MicroAdventures API", urls_namespace="walks_api")
api.add_router("/walks", walks_router)
api.add_router("/users", progress_router)
register_error_handlers(api)


@api.get("/health", response={200: None})
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
