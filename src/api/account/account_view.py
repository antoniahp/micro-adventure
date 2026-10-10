from ninja import Router

from api import wiring
from api.account.account_serializer import AccountOut, GoogleLinkIn, GoogleLinkOut, NicknameIn
from api.auth.session import ensure_own_user, issue_tokens
from microadventures.application.commands.link_google_account.link_google_account_command import LinkGoogleAccountCommand
from microadventures.application.commands.set_nickname.set_nickname_command import SetNicknameCommand
from microadventures.application.commands.unlink_google_account.unlink_google_account_command import (
    UnlinkGoogleAccountCommand,
)
from microadventures.application.queries.find_account.find_account_query import FindAccountQuery

router = Router()  # mounted at /users


def _out(account) -> dict:
    if account is None:
        return {"nickname": None, "google_linked": False}
    return {
        "nickname": account.nickname,
        "google_linked": bool(account.google_sub),
    }


def _find(user_id: str):
    return wiring.find_account_handler().handle(FindAccountQuery(user_id=user_id))


@router.get("/{user_id}/account", response=AccountOut)
def get_account(request, user_id: str):
    ensure_own_user(request, user_id)
    return _out(_find(user_id))


@router.put("/{user_id}/account/nickname", response=AccountOut)
def set_nickname(request, user_id: str, payload: NicknameIn):
    ensure_own_user(request, user_id)
    wiring.set_nickname_handler().handle(SetNicknameCommand(user_id=user_id, nickname=payload.nickname))
    return _out(_find(user_id))


@router.post("/{user_id}/account/google/link", response=GoogleLinkOut)
def link_google(request, user_id: str, payload: GoogleLinkIn):
    ensure_own_user(request, user_id)
    resulting_user_id = wiring.link_google_account_handler().handle(
        LinkGoogleAccountCommand(user_id=user_id, id_token=payload.id_token)
    )
    account = _find(resulting_user_id)
    if resulting_user_id != user_id:
        tokens = issue_tokens(resulting_user_id)
        return {**_out(account), "switched": True, "user_id": resulting_user_id, "access": tokens["access"], "refresh": tokens["refresh"]}
    return {**_out(account), "switched": False, "user_id": user_id, "access": None, "refresh": None}


@router.post("/{user_id}/account/google/unlink", response=AccountOut)
def unlink_google(request, user_id: str):
    ensure_own_user(request, user_id)
    wiring.unlink_google_account_handler().handle(UnlinkGoogleAccountCommand(user_id=user_id))
    return _out(_find(user_id))
