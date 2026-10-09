"""Builds each handler with its real adapters. Routers stay free of infrastructure details."""

import requests
from django.conf import settings

from microadventures.application.queries.find_walk_context.find_walk_context_query_handler import FindWalkContextQueryHandler
from microadventures.domain.services.weather_service import WeatherService
from microadventures.infrastructure.api.open_meteo_weather_service import OpenMeteoWeatherService

from microadventures.application.commands.complete_challenge.complete_challenge_command_handler import CompleteChallengeCommandHandler
from microadventures.application.commands.save_weekly_reflection.save_weekly_reflection_command_handler import SaveWeeklyReflectionCommandHandler
from microadventures.application.queries.find_progress.find_progress_query_handler import FindProgressQueryHandler
from microadventures.application.queries.find_weekly_summary.find_weekly_summary_query_handler import FindWeeklySummaryQueryHandler
from microadventures.application.queries.find_yearly_summary.find_yearly_summary_query_handler import FindYearlySummaryQueryHandler
from microadventures.application.queries.transcribe_audio.transcribe_audio_query_handler import TranscribeAudioQueryHandler
from microadventures.application.queries.find_walk.find_walk_query_handler import FindWalkQueryHandler
from microadventures.application.commands.finish_walk.finish_walk_command_handler import FinishWalkCommandHandler
from microadventures.application.commands.create_telegram_link.create_telegram_link_command_handler import CreateTelegramLinkCommandHandler
from microadventures.application.commands.handle_telegram_callback.handle_telegram_callback_command_handler import HandleTelegramCallbackCommandHandler
from microadventures.application.commands.handle_telegram_message.handle_telegram_message_command_handler import HandleTelegramMessageCommandHandler
from microadventures.application.commands.register_bot_webhook.register_bot_webhook_command_handler import RegisterBotWebhookCommandHandler
from microadventures.application.commands.save_reminder_settings.save_reminder_settings_command_handler import SaveReminderSettingsCommandHandler
from microadventures.application.commands.send_due_reminders.send_due_reminders_command_handler import SendDueRemindersCommandHandler
from microadventures.application.commands.unlink_telegram.unlink_telegram_command_handler import UnlinkTelegramCommandHandler
from microadventures.application.queries.find_reminder_settings.find_reminder_settings_query_handler import FindReminderSettingsQueryHandler
from microadventures.application.commands.start_walk.start_walk_command_handler import StartWalkCommandHandler
from microadventures.application.commands.swap_challenge.swap_challenge_command_handler import SwapChallengeCommandHandler
from microadventures.application.commands.warm_up_generator.warm_up_generator_command_handler import WarmUpGeneratorCommandHandler
from microadventures.domain.services.bot_webhook import BotWebhook
from microadventures.domain.services.challenge_generator import ChallengeGenerator
from microadventures.domain.services.notification_sender import NotificationSender
from microadventures.domain.services.reflection_service import ReflectionService
from microadventures.domain.services.reminder_service import ReminderService
from microadventures.domain.services.photo_verifier import PhotoVerifier
from microadventures.domain.services.speech_transcriber import SpeechTranscriber
from microadventures.domain.services.walk_service import WalkService
from microadventures.infrastructure.fallback_challenge_generator import FallbackChallengeGenerator
from microadventures.infrastructure.api.ollama_challenge_generator import OllamaChallengeGenerator
from microadventures.infrastructure.api.elevenlabs_speech_transcriber import ElevenLabsSpeechTranscriber
from microadventures.infrastructure.api.ollama_photo_verifier import OllamaPhotoVerifier
from microadventures.infrastructure.api.telegram_notification_sender import TelegramNotificationSender
from microadventures.infrastructure.repositories.db_reflection_repository import DbReflectionRepository
from microadventures.infrastructure.repositories.db_reminder_repository import DbReminderRepository
from microadventures.infrastructure.unavailable_notification_sender import UnavailableNotificationSender
from microadventures.infrastructure.repositories.db_walk_repository import DbWalkRepository
from microadventures.infrastructure.template_challenge_generator import TemplateChallengeGenerator
from microadventures.infrastructure.trusting_photo_verifier import TrustingPhotoVerifier
from microadventures.infrastructure.unavailable_speech_transcriber import UnavailableSpeechTranscriber


def _walk_repository() -> WalkService:
    return DbWalkRepository()


def _ollama_http():
    """Ollama has no login of its own. A hosted one sits behind a proxy that expects this key."""
    if not settings.OLLAMA_API_KEY:
        return requests
    session = requests.Session()
    session.headers["Authorization"] = f"Bearer {settings.OLLAMA_API_KEY}"
    return session


def _challenge_generator() -> ChallengeGenerator:
    return FallbackChallengeGenerator(
        primary=OllamaChallengeGenerator(
            base_url=settings.OLLAMA_URL,
            model=settings.OLLAMA_MODEL,
            timeout_seconds=settings.OLLAMA_TIMEOUT_SECONDS,
            http=_ollama_http(),
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
        http=_ollama_http(),
    )


def _reflection_repository() -> ReflectionService:
    return DbReflectionRepository()


_weather_service_instance = OpenMeteoWeatherService()  # one for the whole server, so its short memory is shared


def _weather_service() -> WeatherService:
    return _weather_service_instance


def _reminder_repository() -> ReminderService:
    return DbReminderRepository()


def _notification_sender() -> NotificationSender | BotWebhook:
    if settings.TELEGRAM_BOT_TOKEN:
        return TelegramNotificationSender(token=settings.TELEGRAM_BOT_TOKEN)
    return UnavailableNotificationSender()


def _speech_transcriber() -> SpeechTranscriber:
    if settings.ELEVENLABS_API_KEY:
        return ElevenLabsSpeechTranscriber(api_key=settings.ELEVENLABS_API_KEY, model=settings.ELEVENLABS_STT_MODEL)
    return UnavailableSpeechTranscriber()


def start_walk_handler() -> StartWalkCommandHandler:
    return StartWalkCommandHandler(walk_service=_walk_repository(), challenge_generator=_challenge_generator(), weather_service=_weather_service())


def warm_up_generator_handler() -> WarmUpGeneratorCommandHandler:
    return WarmUpGeneratorCommandHandler(challenge_generator=_challenge_generator())


def complete_challenge_handler() -> CompleteChallengeCommandHandler:
    return CompleteChallengeCommandHandler(walk_service=_walk_repository(), photo_verifier=_photo_verifier())


def finish_walk_handler() -> FinishWalkCommandHandler:
    return FinishWalkCommandHandler(walk_service=_walk_repository())


def swap_challenge_handler() -> SwapChallengeCommandHandler:
    return SwapChallengeCommandHandler(walk_service=_walk_repository(), challenge_generator=_challenge_generator())


def transcribe_audio_handler() -> TranscribeAudioQueryHandler:
    return TranscribeAudioQueryHandler(speech_transcriber=_speech_transcriber())


def find_walk_handler() -> FindWalkQueryHandler:
    return FindWalkQueryHandler(walk_service=_walk_repository())


def find_walk_context_handler() -> FindWalkContextQueryHandler:
    return FindWalkContextQueryHandler(weather_service=_weather_service())


def find_progress_handler() -> FindProgressQueryHandler:
    return FindProgressQueryHandler(walk_service=_walk_repository())


def save_reminder_settings_handler() -> SaveReminderSettingsCommandHandler:
    return SaveReminderSettingsCommandHandler(reminder_service=_reminder_repository(), notification_sender=_notification_sender())


def create_telegram_link_handler() -> CreateTelegramLinkCommandHandler:
    return CreateTelegramLinkCommandHandler(reminder_service=_reminder_repository())


def unlink_telegram_handler() -> UnlinkTelegramCommandHandler:
    return UnlinkTelegramCommandHandler(reminder_service=_reminder_repository())


def handle_telegram_message_handler() -> HandleTelegramMessageCommandHandler:
    return HandleTelegramMessageCommandHandler(reminder_service=_reminder_repository(), notification_sender=_notification_sender())


def handle_telegram_callback_handler() -> HandleTelegramCallbackCommandHandler:
    return HandleTelegramCallbackCommandHandler(reminder_service=_reminder_repository(), notification_sender=_notification_sender())


def send_due_reminders_handler() -> SendDueRemindersCommandHandler:
    return SendDueRemindersCommandHandler(
        reminder_service=_reminder_repository(),
        notification_sender=_notification_sender(),
        app_url=settings.APP_URL,
        weather_service=_weather_service(),
    )


def register_bot_webhook_handler() -> RegisterBotWebhookCommandHandler:
    return RegisterBotWebhookCommandHandler(bot_webhook=_notification_sender())


def find_reminder_settings_handler() -> FindReminderSettingsQueryHandler:
    return FindReminderSettingsQueryHandler(reminder_service=_reminder_repository())


def find_weekly_summary_handler() -> FindWeeklySummaryQueryHandler:
    return FindWeeklySummaryQueryHandler(walk_service=_walk_repository(), reflection_service=_reflection_repository())


def find_yearly_summary_handler() -> FindYearlySummaryQueryHandler:
    return FindYearlySummaryQueryHandler(walk_service=_walk_repository(), reflection_service=_reflection_repository())


def save_weekly_reflection_handler() -> SaveWeeklyReflectionCommandHandler:
    return SaveWeeklyReflectionCommandHandler(reflection_service=_reflection_repository())
