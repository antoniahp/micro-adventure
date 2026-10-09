from datetime import datetime

from ninja import Schema


class ConditionsOut(Schema):
    dark: bool
    rain: bool
    storm: bool
    cold: bool
    hot: bool
    windy: bool


class WalkContextOut(Schema):
    temperature_c: float
    sky: str  # clear, cloudy, fog, rain, snow, storm
    rain_mm: float
    wind_kmh: float
    sunrise: datetime
    sunset: datetime
    minutes_of_light: int
    suggested_weather: str  # sunny, cloudy, rainy: the buttons of the start screen
    conditions: ConditionsOut
