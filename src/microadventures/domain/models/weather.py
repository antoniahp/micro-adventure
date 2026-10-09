from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class Sky(str, Enum):
    CLEAR = "clear"
    CLOUDY = "cloudy"
    FOG = "fog"
    RAIN = "rain"
    SNOW = "snow"
    STORM = "storm"

    @classmethod
    def from_wmo(cls, code: int) -> "Sky":
        """Open-Meteo gives the sky as a WMO weather code: https://open-meteo.com/en/docs"""
        if code in (0, 1):
            return cls.CLEAR
        if code in (2, 3):
            return cls.CLOUDY
        if code in (45, 48):
            return cls.FOG
        if code in (51, 53, 55, 56, 57, 61, 63, 65, 66, 67, 80, 81, 82):
            return cls.RAIN
        if code in (71, 73, 75, 77, 85, 86):
            return cls.SNOW
        if code in (95, 96, 99):
            return cls.STORM
        return cls.CLOUDY


@dataclass(frozen=True)
class Weather:
    """The weather where a person is, now, and when the sun sets there today. Times carry their time zone."""

    temperature_c: float
    sky: Sky
    rain_mm: float
    wind_kmh: float
    sunrise: datetime
    sunset: datetime

    def is_dark(self, now: datetime) -> bool:
        return now < self.sunrise or now >= self.sunset

    def minutes_of_light(self, now: datetime) -> int:
        """Minutes until the sun sets. Zero once it is dark."""
        if self.is_dark(now):
            return 0
        return int((self.sunset - now).total_seconds() // 60)
