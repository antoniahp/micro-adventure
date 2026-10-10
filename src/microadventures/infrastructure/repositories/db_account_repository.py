from django.db import IntegrityError
from pymongo.errors import DuplicateKeyError

from core.email_hash import hash_email
from microadventures.domain.models.account import Account
from microadventures.domain.services.account_service import AccountService


class DbAccountRepository(AccountService):
    def claim(self, user_id: str) -> bool:
        if Account.objects.filter(user_id=user_id).exists():
            return False
        try:
            Account.objects.create(user_id=user_id)
        except (IntegrityError, DuplicateKeyError):
            return False  # two requests claimed it at the same time: the unique index let only one in
        return True

    def find_by_user_id(self, user_id: str) -> Account | None:
        return Account.objects.filter(user_id=user_id).first()

    def set_nickname(self, user_id: str, nickname: str | None) -> None:
        Account.objects.filter(user_id=user_id).update(nickname=nickname)

    def find_by_google_sub(self, google_sub: str) -> Account | None:
        return Account.objects.filter(google_sub=google_sub).first()

    def link_google(self, user_id: str, google_sub: str, google_email: str) -> None:
        # The real address never reaches the database: only a one-way hash, enough to tell "same
        # Google account as before" apart from a different one, never enough to recover the address.
        Account.objects.filter(user_id=user_id).update(google_sub=google_sub, google_email_hash=hash_email(google_email))

    def unlink_google(self, user_id: str) -> None:
        Account.objects.filter(user_id=user_id).update(google_sub=None, google_email_hash=None)
