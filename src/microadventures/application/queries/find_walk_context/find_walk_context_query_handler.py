from microadventures.application.queries.find_walk_context.find_walk_context_query import FindWalkContextQuery
from microadventures.application.queries.find_walk_context.walk_context import WalkContext
from microadventures.domain.models.conditions import Conditions
from microadventures.domain.services.weather_service import WeatherService


class FindWalkContextQueryHandler:
    def __init__(self, weather_service: WeatherService):
        self.weather_service = weather_service

    def handle(self, query: FindWalkContextQuery) -> WalkContext:
        weather = self.weather_service.at(query.latitude, query.longitude)
        return WalkContext(
            temperature_c=weather.temperature_c,
            sky=weather.sky,
            rain_mm=weather.rain_mm,
            wind_kmh=weather.wind_kmh,
            sunrise=weather.sunrise,
            sunset=weather.sunset,
            minutes_of_light=weather.minutes_of_light(query.now),
            conditions=Conditions.from_weather(weather, query.now),
        )
