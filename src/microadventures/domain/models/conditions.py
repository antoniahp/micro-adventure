from dataclasses import dataclass
from datetime import datetime

from microadventures.domain.models.language import Language
from microadventures.domain.models.weather import Sky, Weather

COLD_BELOW_C = 5
HOT_ABOVE_C = 32
WINDY_ABOVE_KMH = 35
LITTLE_LIGHT_MINUTES = 30  # the last half hour before sunset already feels like evening


@dataclass(frozen=True)
class Conditions:
    """What the weather and the hour ask of a walk. They decide which challenges are safe to suggest."""

    dark: bool = False
    rain: bool = False
    storm: bool = False
    cold: bool = False
    hot: bool = False
    windy: bool = False

    @classmethod
    def from_weather(cls, weather: Weather, now: datetime) -> "Conditions":
        return cls(
            dark=weather.is_dark(now) or weather.minutes_of_light(now) < LITTLE_LIGHT_MINUTES,
            rain=weather.sky in (Sky.RAIN, Sky.SNOW, Sky.STORM) or weather.rain_mm >= 0.5,
            storm=weather.sky == Sky.STORM,
            cold=weather.temperature_c < COLD_BELOW_C,
            hot=weather.temperature_c > HOT_ABOVE_C,
            windy=weather.wind_kmh > WINDY_ABOVE_KMH,
        )

    @classmethod
    def from_text(cls, text: str) -> "Conditions":
        names = set(text.split(",")) if text else set()
        return cls(**{name: name in names for name in cls.__dataclass_fields__})

    def to_text(self) -> str:
        return ",".join(name for name in self.__dataclass_fields__ if getattr(self, name))

    @property
    def needs_calm_walk(self) -> bool:
        """After dark or under rain the challenges stay on lit, busy or covered places."""
        return self.dark or self.rain

    def guidance(self, language: Language) -> str:
        """Rules for the model, written in the language of the prompt. Empty when nothing special applies."""
        rules = GUIDANCE[language]
        return " ".join(rules[name] for name in self.__dataclass_fields__ if getattr(self, name))


GUIDANCE = {
    Language.ES: {
        "dark": "Es de noche o casi: solo retos en calles con luz y con gente, sin parques, descampados ni caminos solitarios, y sin pedir que se alejen de la ruta. ",
        "rain": "Llueve: retos cortos y que se puedan hacer bajo cubierto o sin pararse (un portal, una marquesina, escuchar la lluvia). ",
        "storm": "Hay tormenta: solo retos que se hagan desde un lugar cubierto y seguro, sin árboles ni zonas abiertas. ",
        "cold": "Hace frío: retos que mantengan en movimiento, sin pedir quedarse quieto mucho rato. ",
        "hot": "Hace mucho calor: retos a la sombra y cerca de agua o fuentes, sin esfuerzo. ",
        "windy": "Hace mucho viento: nada junto a árboles grandes ni obras. ",
    },
    Language.EN: {
        "dark": "It is dark or nearly: only challenges on lit, busy streets, no parks, waste ground or lonely paths, and never ask to leave the route. ",
        "rain": "It is raining: short challenges that can be done under cover or while moving (a doorway, a bus shelter, listening to the rain). ",
        "storm": "There is a storm: only challenges done from a covered, safe place, away from trees and open ground. ",
        "cold": "It is cold: challenges that keep people moving, without standing still for long. ",
        "hot": "It is very hot: challenges in the shade and near water or fountains, without effort. ",
        "windy": "It is very windy: nothing next to big trees or building sites. ",
    },
}
