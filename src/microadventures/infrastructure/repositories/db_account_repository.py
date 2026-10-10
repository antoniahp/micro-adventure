from django.db import IntegrityError
from pymongo.errors import DuplicateKeyError

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
