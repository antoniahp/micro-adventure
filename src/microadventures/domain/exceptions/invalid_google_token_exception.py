class InvalidGoogleTokenException(Exception):
    """Google would not vouch for the credential: it is missing, expired, forged, or for a different app."""

    def __init__(self):
        super().__init__("Could not verify the Google sign-in")
