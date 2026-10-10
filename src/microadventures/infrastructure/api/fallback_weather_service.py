import logging

from microadventures.domain.exceptions.weather_unavailable_exception import WeatherUnavailableException
from microadventures.domain.models.weather import Weather
from microadventures.domain.services.weather_service import WeatherService

logger = logging.getLogger(__name__)


class FallbackWeatherService(WeatherService):
    """Asks the first service and, if it cannot answer (a busy shared address gets "429"), the second one."""

    def __init__(self, primary: WeatherService, fallback: WeatherService):
        self.primary = primary
        self.fallback = fallback

    def at(self, latitude: float, longitude: float) -> Weather:
        try:
            return self.primary.at(latitude, longitude)
        except WeatherUnavailableException as error:
            logger.warning("🛟 Primary weather failed, trying the backup: %s", error)
            return self.fallback.at(latitude, longitude)
