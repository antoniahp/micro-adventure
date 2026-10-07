from abc import ABC, abstractmethod
from uuid import UUID

from microadventures.domain.services.walk_criteria import WalkCriteria
from microadventures.domain.models.walk import Walk


class WalkService(ABC):
    @abstractmethod
    def save(self, walk: Walk) -> None:
        raise NotImplementedError

    @abstractmethod
    def find_by_criteria(self, criteria: WalkCriteria) -> list[Walk]:
        raise NotImplementedError

    @abstractmethod
    def find_or_fail_by_id(self, id: UUID) -> Walk:
        raise NotImplementedError
