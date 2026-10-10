import logging
import time
from datetime import datetime, timedelta, timezone

import requests

from microadventures.domain.exceptions.weather_unavailable_exception import WeatherUnavailableException
from microadventures.domain.models.weather import Sky, Weather
from microadventures.domain.services.weather_service import WeatherService

URL = "https://api.open-meteo.com/v1/forecast"
logger = logging.getLogger(__name__)
CACHE_SECONDS = 1800  # the weather barely changes in half an hour, and the service is free: be kind to it
BUSY_SECONDS = 300  # after a "429 too many requests" do not ask again for five minutes
FAILURE_SECONDS = 60  # any other failure is remembered briefly so a retrying page does not hammer the service


class OpenMeteoWeatherService(WeatherService):
    """https://open-meteo.com: free, no key. Places are rounded to about a kilometre, which is all the weather needs."""

    def __init__(self, http=requests, timeout_seconds: float = 6, clock=time.monotonic):
        self.http = http
        self.timeout_seconds = timeout_seconds
        self.clock = clock
        self._cache: dict[tuple[float, float], tuple[float, Weather | WeatherUnavailableException]] = {}

    def at(self, latitude: float, longitude: float) -> Weather:
        place = (round(latitude, 2), round(longitude, 2))
        cached = self._cache.get(place)
        if cached and self.clock() - cached[0] < _remembered_for(cached[1]):
            if isinstance(cached[1], WeatherUnavailableException):
                raise cached[1]  # the failure is remembered too: no new request until it expires
            return cached[1]
        try:
            weather = self._fetch(*place)
        except WeatherUnavailableException as error:
            self._cache[place] = (self.clock(), error)
            raise
        logger.info("🌤️ Weather at %s: %s, %.0f°C", place, weather.sky.value, weather.temperature_c)
        self._cache[place] = (self.clock(), weather)
        return weather

    def _fetch(self, latitude: float, longitude: float) -> Weather:
        try:
            response = self.http.get(
                URL,
                params={
                    "latitude": latitude,
                    "longitude": longitude,
                    "current": "temperature_2m,precipitation,weather_code,wind_speed_10m",
                    "daily": "sunrise,sunset",
                    "timezone": "auto",
                    "forecast_days": 1,
                },
                headers={"User-Agent": "MicroAdventures/1.0 (+https://micro-adventure.onrender.com)"},
                timeout=self.timeout_seconds,
            )
            response.raise_for_status()
            return _parse(response.json())
        except (requests.RequestException, ValueError, KeyError, IndexError, TypeError) as error:
            status = getattr(getattr(error, "response", None), "status_code", None)
            raise WeatherUnavailableException(f"{type(error).__name__} {status}" if status else type(error).__name__) from error


def _remembered_for(answer) -> int:
    if isinstance(answer, WeatherUnavailableException):
        return BUSY_SECONDS if " 429" in str(answer) else FAILURE_SECONDS
    return CACHE_SECONDS


def _parse(body: dict) -> Weather:
    offset = timezone(timedelta(seconds=body["utc_offset_seconds"]))  # "timezone=auto" gives local times
    current, daily = body["current"], body["daily"]
    return Weather(
        temperature_c=float(current["temperature_2m"]),
        sky=Sky.from_wmo(int(current["weather_code"])),
        rain_mm=float(current["precipitation"]),
        wind_kmh=float(current["wind_speed_10m"]),
        sunrise=datetime.fromisoformat(daily["sunrise"][0]).replace(tzinfo=offset),
        sunset=datetime.fromisoformat(daily["sunset"][0]).replace(tzinfo=offset),
    )
