from microadventures.domain.models.challenge import Challenge
from microadventures.domain.models.photo_verdict import PhotoVerdict
from microadventures.domain.services.photo_verifier import PhotoVerifier


class TrustingPhotoVerifier(PhotoVerifier):
    """Accepts every photo. Plan B when the vision model is slow or unavailable."""

    def verify(self, challenge: Challenge, photo: bytes) -> PhotoVerdict:
        return PhotoVerdict(accepted=True)
