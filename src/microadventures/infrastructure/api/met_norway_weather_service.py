import logging
import time
from datetime import datetime, timedelta, timezone

import requests

from microadventures.domain.exceptions.weather_unavailable_exception import WeatherUnavailableException
from microadventures.domain.models.sun import sun_times
from microadventures.domain.models.weather import Sky, Weather
from microadventures.domain.services.weather_service import WeatherService

logger = logging.getLogger(__name__)

URL = "https://api.met.no/weatherapi/locationforecast/2.0/compact"
USER_AGENT = "MicroAdventures/1.0 (+https://micro-adventure.onrender.com)"  # MET Norway asks every app to identify itself
CACHE_SECONDS = 1800
FAILURE_SECONDS = 300


class MetNorwayWeatherService(WeatherService):
    """https://api.met.no: free, no key. It does not say when the sun sets, so that is worked out from the place."""

    def __init__(self, http=requests, timeout_seconds: float = 6, clock=time.monotonic, utc_now=lambda: datetime.now(timezone.utc)):
        self.http = http
        self.timeout_seconds = timeout_seconds
        self.clock = clock
        self.utc_now = utc_now
        self._cache: dict[tuple[float, float], tuple[float, Weather | WeatherUnavailableException]] = {}

    def at(self, latitude: float, longitude: float) -> Weather:
        place = (round(latitude, 2), round(longitude, 2))
        cached = self._cache.get(place)
        if cached and self.clock() - cached[0] < (FAILURE_SECONDS if isinstance(cached[1], Exception) else CACHE_SECONDS):
            if isinstance(cached[1], Exception):
                raise cached[1]
            return cached[1]
        try:
            weather = self._fetch(*place)
        except WeatherUnavailableException as error:
            self._cache[place] = (self.clock(), error)
            raise
        self._cache[place] = (self.clock(), weather)
        logger.info("🌤️ Weather at %s from MET Norway: %s, %.0f°C", place, weather.sky.value, weather.temperature_c)
        return weather

    def _fetch(self, latitude: float, longitude: float) -> Weather:
        try:
            response = self.http.get(
                URL,
                params={"lat": latitude, "lon": longitude},
                headers={"User-Agent": USER_AGENT},
                timeout=self.timeout_seconds,
            )
            response.raise_for_status()
            return self._parse(response.json(), latitude, longitude)
        except (requests.RequestException, ValueError, KeyError, IndexError, TypeError) as error:
            status = getattr(getattr(error, "response", None), "status_code", None)
            raise WeatherUnavailableException(f"MET Norway {type(error).__name__} {status}" if status else f"MET Norway {type(error).__name__}") from error

    def _parse(self, body: dict, latitude: float, longitude: float) -> Weather:
        entry = body["properties"]["timeseries"][0]["data"]
        details = entry["instant"]["details"]
        ahead = entry.get("next_1_hours") or entry["next_6_hours"]
        solar_day = (self.utc_now() + timedelta(hours=longitude / 15)).date()
        sunrise, sunset = sun_times(latitude, longitude, solar_day)
        return Weather(
            temperature_c=float(details["air_temperature"]),
            sky=_sky(ahead["summary"]["symbol_code"]),
            rain_mm=float(ahead.get("details", {}).get("precipitation_amount", 0)),
            wind_kmh=round(float(details["wind_speed"]) * 3.6, 1),  # it speaks in metres per second
            sunrise=sunrise,
            sunset=sunset,
        )


def _sky(symbol: str) -> Sky:
    """Symbols look like "partlycloudy_day" or "heavyrainandthunder": https://api.met.no/weatherapi/weathericon/2.0/documentation"""
    if "thunder" in symbol:
        return Sky.STORM
    if "snow" in symbol or "sleet" in symbol:
        return Sky.SNOW
    if "rain" in symbol or "showers" in symbol:
        return Sky.RAIN
    if "fog" in symbol:
        return Sky.FOG
    if symbol.startswith(("clearsky", "fair")):
        return Sky.CLEAR
    return Sky.CLOUDY
