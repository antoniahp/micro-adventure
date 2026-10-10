from microadventures.application.queries.find_account.find_account_query import FindAccountQuery
from microadventures.domain.services.account_service import AccountLike, AccountService


class FindAccountQueryHandler:
    def __init__(self, account_service: AccountService):
        self.account_service = account_service

    def handle(self, query: FindAccountQuery) -> AccountLike | None:
        return self.account_service.find_by_user_id(query.user_id)
