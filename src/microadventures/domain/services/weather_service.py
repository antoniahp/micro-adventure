from abc import ABC, abstractmethod

from microadventures.domain.models.weather import Weather


class WeatherService(ABC):
    """Tells the weather at a place. Raises WeatherUnavailableException when it cannot."""

    @abstractmethod
    def at(self, latitude: float, longitude: float) -> Weather:
        raise NotImplementedError
