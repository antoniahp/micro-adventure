"""Builds each handler with its real adapters. Routers stay free of infrastructure details."""

from django.conf import settings

from microadventures.application.commands.complete_challenge.complete_challenge_command_handler import CompleteChallengeCommandHandler
from microadventures.application.queries.find_progress.find_progress_query_handler import FindProgressQueryHandler
from microadventures.application.queries.transcribe_audio.transcribe_audio_query_handler import TranscribeAudioQueryHandler
from microadventures.application.queries.find_walk.find_walk_query_handler import FindWalkQueryHandler
from microadventures.application.commands.start_walk.start_walk_command_handler import StartWalkCommandHandler
from microadventures.application.commands.swap_challenge.swap_challenge_command_handler import SwapChallengeCommandHandler
from microadventures.application.commands.warm_up_generator.warm_up_generator_command_handler import WarmUpGeneratorCommandHandler
from microadventures.domain.services.challenge_generator import ChallengeGenerator
from microadventures.domain.services.photo_verifier import PhotoVerifier
from microadventures.domain.services.speech_transcriber import SpeechTranscriber
from microadventures.domain.services.walk_service import WalkService
from microadventures.infrastructure.fallback_challenge_generator import FallbackChallengeGenerator
from microadventures.infrastructure.api.ollama_challenge_generator import OllamaChallengeGenerator
from microadventures.infrastructure.api.elevenlabs_speech_transcriber import ElevenLabsSpeechTranscriber
from microadventures.infrastructure.api.ollama_photo_verifier import OllamaPhotoVerifier
from microadventures.infrastructure.repositories.db_walk_repository import DbWalkRepository
from microadventures.infrastructure.template_challenge_generator import TemplateChallengeGenerator
from microadventures.infrastructure.trusting_photo_verifier import TrustingPhotoVerifier
from microadventures.infrastructure.unavailable_speech_transcriber import UnavailableSpeechTranscriber


def _walk_repository() -> WalkService:
    return DbWalkRepository()


def _challenge_generator() -> ChallengeGenerator:
    return FallbackChallengeGenerator(
        primary=OllamaChallengeGenerator(
            base_url=settings.OLLAMA_URL,
            model=settings.OLLAMA_MODEL,
            timeout_seconds=settings.OLLAMA_TIMEOUT_SECONDS,
        ),
        fallback=TemplateChallengeGenerator(),
    )


def _photo_verifier() -> PhotoVerifier:
    if settings.PHOTO_VERIFIER == "trusting":
        return TrustingPhotoVerifier()
    return OllamaPhotoVerifier(
        base_url=settings.OLLAMA_URL,
        model=settings.OLLAMA_VISION_MODEL,
        timeout_seconds=settings.OLLAMA_TIMEOUT_SECONDS,
    )


def _speech_transcriber() -> SpeechTranscriber:
    if settings.ELEVENLABS_API_KEY:
        return ElevenLabsSpeechTranscriber(api_key=settings.ELEVENLABS_API_KEY, model=settings.ELEVENLABS_STT_MODEL)
    return UnavailableSpeechTranscriber()


def start_walk_handler() -> StartWalkCommandHandler:
    return StartWalkCommandHandler(walk_service=_walk_repository(), challenge_generator=_challenge_generator())


def warm_up_generator_handler() -> WarmUpGeneratorCommandHandler:
    return WarmUpGeneratorCommandHandler(challenge_generator=_challenge_generator())


def complete_challenge_handler() -> CompleteChallengeCommandHandler:
    return CompleteChallengeCommandHandler(walk_service=_walk_repository(), photo_verifier=_photo_verifier())


def swap_challenge_handler() -> SwapChallengeCommandHandler:
    return SwapChallengeCommandHandler(walk_service=_walk_repository(), challenge_generator=_challenge_generator())


def transcribe_audio_handler() -> TranscribeAudioQueryHandler:
    return TranscribeAudioQueryHandler(speech_transcriber=_speech_transcriber())


def find_walk_handler() -> FindWalkQueryHandler:
    return FindWalkQueryHandler(walk_service=_walk_repository())


def find_progress_handler() -> FindProgressQueryHandler:
    return FindProgressQueryHandler(walk_service=_walk_repository())
