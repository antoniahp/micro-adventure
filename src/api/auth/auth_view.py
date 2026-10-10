from uuid import uuid4

from ninja import Router

from api import wiring
from api.auth.auth_serializer import RefreshIn, SessionOut, StartSessionIn
from api.auth.session import issue_tokens, renew_tokens
from microadventures.application.commands.claim_account.claim_account_command import ClaimAccountCommand

router = Router(tags=["auth"], auth=None)


@router.post("/start", response=SessionOut)
def start_session(request, payload: StartSessionIn):
    """The first visit of a browser. It sends the id it used before (if any) and gets its tokens, once."""
    user_id = payload.user_id or str(uuid4())
    wiring.claim_account_handler().handle(ClaimAccountCommand(user_id=user_id))
    return issue_tokens(user_id)


@router.post("/refresh", response=SessionOut)
def refresh_session(request, payload: RefreshIn):
    return renew_tokens(payload.refresh)
