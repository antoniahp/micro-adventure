from dataclasses import dataclass
from datetime import datetime

from microadventures.domain.models.conditions import Conditions
from microadventures.domain.models.weather import Sky


@dataclass(frozen=True)
class WalkContext:
    """What the person needs to know before going out: the weather, the light that is left and what it asks of the walk."""

    temperature_c: float
    sky: Sky
    rain_mm: float
    wind_kmh: float
    sunrise: datetime
    sunset: datetime
    minutes_of_light: int
    conditions: Conditions

    @property
    def suggested_weather(self) -> str:
        """The value of the weather buttons of the start screen."""
        if self.conditions.rain:
            return "rainy"
        return "sunny" if self.sky == Sky.CLEAR else "cloudy"
