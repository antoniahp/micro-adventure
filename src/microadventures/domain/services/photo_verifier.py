from abc import ABC, abstractmethod

from microadventures.domain.models.challenge import Challenge
from microadventures.domain.models.photo_verdict import PhotoVerdict


class PhotoVerifier(ABC):
    @abstractmethod
    def verify(self, challenge: Challenge, photo: bytes) -> PhotoVerdict:
        raise NotImplementedError
