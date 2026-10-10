from abc import ABC, abstractmethod
from typing import Protocol


class AccountLike(Protocol):
    """What callers need from an account record, whether it's a real Account or a test double."""

    user_id: str
    nickname: str | None
    google_sub: str | None
    # No email field here, on purpose: nothing above the repository ever needs the real address,
    # only whether a Google account is linked (google_sub) — see core/email_hash.py.


class AccountService(ABC):
    @abstractmethod
    def claim(self, user_id: str) -> bool:
        """Registers the id. False when someone already did (nothing changes)."""
        raise NotImplementedError

    @abstractmethod
    def find_by_user_id(self, user_id: str) -> AccountLike | None:
        raise NotImplementedError

    @abstractmethod
    def set_nickname(self, user_id: str, nickname: str | None) -> None:
        raise NotImplementedError

    @abstractmethod
    def find_by_google_sub(self, google_sub: str) -> AccountLike | None:
        raise NotImplementedError

    @abstractmethod
    def link_google(self, user_id: str, google_sub: str, google_email: str) -> None:
        raise NotImplementedError

    @abstractmethod
    def unlink_google(self, user_id: str) -> None:
        raise NotImplementedError
