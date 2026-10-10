from abc import ABC, abstractmethod


class GoogleIdentityVerifier(ABC):
    @abstractmethod
    def verify(self, id_token: str) -> tuple[str, str]:
        """Checks the credential with Google and returns (sub, email).

        Raises InvalidGoogleTokenException when it cannot be trusted: wrong signature, expired,
        meant for a different app, or the email isn't a verified one.
        """
        raise NotImplementedError
