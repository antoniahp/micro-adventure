class WeatherUnavailableException(Exception):
    """The weather service did not answer. The app goes on without it."""

    def __init__(self, reason: str = ""):
        super().__init__(f"The weather is not available{': ' + reason if reason else ''}")
