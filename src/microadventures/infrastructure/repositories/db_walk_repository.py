from uuid import UUID

from microadventures.domain.exceptions.walk_not_found_exception import WalkNotFoundException
from microadventures.domain.services.walk_criteria import WalkCriteria
from microadventures.domain.services.walk_service import WalkService
from microadventures.domain.models.walk import Walk


class DbWalkRepository(WalkService):
    def save(self, walk: Walk) -> None:
        walk.save()

    def find_by_criteria(self, criteria: WalkCriteria) -> list[Walk]:
        queryset = Walk.objects.all()

        if criteria.id is not None:
            queryset = queryset.filter(id=criteria.id)
        if criteria.user_id is not None:
            queryset = queryset.filter(user_id=criteria.user_id)

        return list(queryset)

    def find_or_fail_by_id(self, id: UUID) -> Walk:
        try:
            return Walk.objects.get(id=id)
        except Walk.DoesNotExist:
            raise WalkNotFoundException(id)
