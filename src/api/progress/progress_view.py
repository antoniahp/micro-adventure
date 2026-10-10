from ninja import Router

from api import wiring
from api.auth.session import ensure_own_user
from api.progress.progress_serializer import ProgressOut
from microadventures.application.queries.find_progress.find_progress_query import FindProgressQuery

router = Router()


@router.get("/{user_id}/progress", response=ProgressOut)
def get_progress(request, user_id: str, timezone: str = "UTC"):
    ensure_own_user(request, user_id)
    return wiring.find_progress_handler().handle(FindProgressQuery(user_id=user_id, timezone=timezone))
