from ninja import NinjaAPI

from microadventures.domain.exceptions.challenge_already_completed_exception import ChallengeAlreadyCompletedException
from microadventures.domain.exceptions.challenge_generation_failed_exception import ChallengeGenerationFailedException
from microadventures.domain.exceptions.challenge_not_found_exception import ChallengeNotFoundException
from microadventures.domain.exceptions.photo_rejected_exception import PhotoRejectedException
from microadventures.domain.exceptions.challenge_response_required_exception import ChallengeResponseRequiredException
from microadventures.domain.exceptions.photo_verification_failed_exception import PhotoVerificationFailedException
from microadventures.domain.exceptions.speech_transcription_failed_exception import SpeechTranscriptionFailedException
from microadventures.domain.exceptions.speech_transcription_unavailable_exception import SpeechTranscriptionUnavailableException
from microadventures.domain.exceptions.swap_limit_reached_exception import SwapLimitReachedException
from microadventures.domain.exceptions.walk_not_found_exception import WalkNotFoundException

STATUS_BY_EXCEPTION = {
    WalkNotFoundException: 404,
    ChallengeNotFoundException: 404,
    ChallengeAlreadyCompletedException: 409,
    SwapLimitReachedException: 409,
    ChallengeResponseRequiredException: 422,
    PhotoRejectedException: 422,
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
        return api.create_response(request, {"detail": str(exception)}, status=status)

    return handler
