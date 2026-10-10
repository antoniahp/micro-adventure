class AccountAlreadyClaimedException(Exception):
    def __init__(self):
        super().__init__("This account already has a session. Use the refresh token you were given.")
