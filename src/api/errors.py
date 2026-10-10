from ninja import NinjaAPI

from microadventures.domain.exceptions.account_already_claimed_exception import AccountAlreadyClaimedException
from microadventures.domain.exceptions.invalid_google_token_exception import InvalidGoogleTokenException
from microadventures.domain.exceptions.challenge_already_completed_exception import ChallengeAlreadyCompletedException
from microadventures.domain.exceptions.challenge_generation_failed_exception import ChallengeGenerationFailedException
from microadventures.domain.exceptions.challenge_not_found_exception import ChallengeNotFoundException
from microadventures.domain.exceptions.invalid_challenges_count_exception import InvalidChallengesCountException
from microadventures.domain.exceptions.invalid_reminder_settings_exception import InvalidReminderSettingsException
from microadventures.domain.exceptions.invalid_weekly_reflection_exception import InvalidWeeklyReflectionException
from microadventures.domain.exceptions.notification_failed_exception import NotificationFailedException
from microadventures.domain.exceptions.notification_unavailable_exception import NotificationUnavailableException
from microadventures.domain.exceptions.photo_rejected_exception import PhotoRejectedException
from microadventures.domain.exceptions.photo_too_large_exception import PhotoTooLargeException
from microadventures.domain.exceptions.challenge_response_required_exception import ChallengeResponseRequiredException
from microadventures.domain.exceptions.photo_verification_failed_exception import PhotoVerificationFailedException
from microadventures.domain.exceptions.speech_transcription_failed_exception import SpeechTranscriptionFailedException
from microadventures.domain.exceptions.speech_transcription_unavailable_exception import SpeechTranscriptionUnavailableException
from microadventures.domain.exceptions.swap_limit_reached_exception import SwapLimitReachedException
from microadventures.domain.exceptions.walk_not_found_exception import WalkNotFoundException
from microadventures.domain.exceptions.weather_unavailable_exception import WeatherUnavailableException

STATUS_BY_EXCEPTION = {
    AccountAlreadyClaimedException: 409,
    InvalidGoogleTokenException: 401,
    WalkNotFoundException: 404,
    ChallengeNotFoundException: 404,
    ChallengeAlreadyCompletedException: 409,
    SwapLimitReachedException: 409,
    ChallengeResponseRequiredException: 422,
    InvalidReminderSettingsException: 422,
    InvalidWeeklyReflectionException: 422,
    NotificationFailedException: 502,
    NotificationUnavailableException: 503,
    WeatherUnavailableException: 503,
    InvalidChallengesCountException: 422,
    PhotoRejectedException: 422,
    PhotoTooLargeException: 422,
    PhotoVerificationFailedException: 502,
    ChallengeGenerationFailedException: 502,
    SpeechTranscriptionFailedException: 502,
    SpeechTranscriptionUnavailableException: 503,
}


def register_error_handlers(api: NinjaAPI) -> None:
    for exception_class, status in STATUS_BY_EXCEPTION.items():
        api.exception_handler(exception_class)(_handler_for(api, status))


def _handler_for(api: NinjaAPI, status: int):
    def handler(request, exception):
        # What went wrong inside (a model, a provider) is for the logs. The person only gets it for 4xx.
        detail = str(exception) if status < 500 else "Service unavailable"
        return api.create_response(request, {"detail": detail}, status=status)

    return handler
