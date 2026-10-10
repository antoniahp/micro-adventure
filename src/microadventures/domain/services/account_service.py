from abc import ABC, abstractmethod


class AccountService(ABC):
    @abstractmethod
    def claim(self, user_id: str) -> bool:
        """Registers the id. False when someone already did (nothing changes)."""
        raise NotImplementedError
