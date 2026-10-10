from datetime import date, datetime, timezone

import pytest
import requests

from microadventures.domain.exceptions.weather_unavailable_exception import WeatherUnavailableException
from microadventures.domain.models.sun import sun_times
from microadventures.domain.models.weather import Sky
from microadventures.infrastructure.api.fallback_weather_service import FallbackWeatherService
from microadventures.infrastructure.api.met_norway_weather_service import MetNorwayWeatherService
from tests.fakes import FakeWeatherService
from tests.microadventures.object_mothers import a_weather

NOW = datetime(2026, 10, 10, 9, 0, tzinfo=timezone.utc)
ANSWER = {
    "properties": {
        "timeseries": [
            {
                "data": {
                    "instant": {"details": {"air_temperature": 14.5, "wind_speed": 2.0}},
                    "next_1_hours": {"summary": {"symbol_code": "partlycloudy_day"}, "details": {"precipitation_amount": 0.2}},
                }
            }
        ]
    }
}


class FakeGet:
    def __init__(self, body=None, status_code=200):
        self.body, self.status_code, self.calls = body or ANSWER, status_code, 0

    def get(self, url, params, headers, timeout):
        self.calls += 1
        assert "User-Agent" in headers
        return self

    def raise_for_status(self):
        if self.status_code != 200:
            raise requests.HTTPError(str(self.status_code), response=self)

    def json(self):
        return self.body


def test_the_sun_times_match_a_known_day_in_madrid():
    sunrise, sunset = sun_times(40.42, -3.7, date(2026, 10, 10))

    assert abs((sunrise - datetime(2026, 10, 10, 6, 20, tzinfo=timezone.utc)).total_seconds()) < 240  # 08:20 in Madrid
    assert abs((sunset - datetime(2026, 10, 10, 17, 42, tzinfo=timezone.utc)).total_seconds()) < 240  # 19:42 in Madrid


def test_in_the_polar_night_there_is_no_light_and_in_midnight_sun_all_day():
    rise, sunset = sun_times(78.2, 15.6, date(2026, 12, 21))
    assert rise == sunset
    rise, sunset = sun_times(78.2, 15.6, date(2026, 6, 21))
    assert (sunset - rise).total_seconds() == 86400


def test_it_reads_met_norway_and_converts_the_wind_to_kmh():
    weather = MetNorwayWeatherService(http=FakeGet(), utc_now=lambda: NOW).at(40.42, -3.7)

    assert (weather.temperature_c, weather.sky, weather.wind_kmh, weather.rain_mm) == (14.5, Sky.CLOUDY, 7.2, 0.2)
    assert weather.sunrise < NOW < weather.sunset


@pytest.mark.parametrize("symbol, sky", [("clearsky_night", Sky.CLEAR), ("heavyrainandthunder", Sky.STORM), ("lightsleet", Sky.SNOW), ("rainshowers_day", Sky.RAIN), ("fog", Sky.FOG)])
def test_symbols_become_skies(symbol, sky):
    body = {"properties": {"timeseries": [{"data": {"instant": {"details": {"air_temperature": 1, "wind_speed": 1}}, "next_1_hours": {"summary": {"symbol_code": symbol}}}}]}}
    assert MetNorwayWeatherService(http=FakeGet(body), utc_now=lambda: NOW).at(40.4, -3.7).sky == sky


def test_the_backup_is_used_only_when_the_first_service_fails():
    working, backup = FakeWeatherService(a_weather()), FakeWeatherService(a_weather(temperature_c=3))

    assert FallbackWeatherService(working, backup).at(1, 1).temperature_c != 3

    class Busy:
        def at(self, latitude, longitude):
            raise WeatherUnavailableException("HTTPError 429")

    assert FallbackWeatherService(Busy(), backup).at(1, 1).temperature_c == 3


def test_a_failing_met_norway_is_remembered_too():
    http = FakeGet(status_code=500)
    service = MetNorwayWeatherService(http=http, utc_now=lambda: NOW)
    for _ in range(3):
        with pytest.raises(WeatherUnavailableException):
            service.at(40.4, -3.7)
    assert http.calls == 1
