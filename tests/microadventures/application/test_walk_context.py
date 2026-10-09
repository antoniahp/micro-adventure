from datetime import datetime, timezone
from uuid import uuid4

from tests.fakes import FakeWeatherService, InMemoryWalkRepository, StubChallengeGenerator
from tests.microadventures.object_mothers import a_challenge, a_walk, a_weather
from microadventures.application.commands.start_walk.start_walk_command import StartWalkCommand
from microadventures.application.commands.start_walk.start_walk_command_handler import StartWalkCommandHandler
from microadventures.application.commands.swap_challenge.swap_challenge_command import SwapChallengeCommand
from microadventures.application.commands.swap_challenge.swap_challenge_command_handler import SwapChallengeCommandHandler
from microadventures.application.queries.find_walk_context.find_walk_context_query import FindWalkContextQuery
from microadventures.application.queries.find_walk_context.find_walk_context_query_handler import FindWalkContextQueryHandler
from microadventures.domain.models.conditions import Conditions
from microadventures.domain.models.language import Language
from microadventures.domain.models.mood import Mood
from microadventures.domain.models.weather import Sky
from microadventures.infrastructure.template_challenge_generator import CALM_TEXTS, CHALLENGE_TEXTS, TemplateChallengeGenerator

AFTERNOON = datetime(2026, 10, 9, 16, 0, tzinfo=timezone.utc)  # 18:00 in Madrid, 1 h 42 min of light left
NIGHT = datetime(2026, 10, 9, 19, 0, tzinfo=timezone.utc)  # 21:00 in Madrid


# --- the weather ---

def test_the_wmo_codes_become_a_sky():
    assert [Sky.from_wmo(code) for code in (0, 3, 45, 61, 75, 95, 1234)] == [Sky.CLEAR, Sky.CLOUDY, Sky.FOG, Sky.RAIN, Sky.SNOW, Sky.STORM, Sky.CLOUDY]


def test_it_counts_the_light_that_is_left_and_none_once_the_sun_has_set():
    weather = a_weather()

    assert weather.minutes_of_light(AFTERNOON) == 102
    assert weather.minutes_of_light(NIGHT) == 0 and weather.is_dark(NIGHT)
    assert weather.is_dark(datetime(2026, 10, 9, 4, 0, tzinfo=timezone.utc))  # before sunrise


# --- what the weather asks of a walk ---

def test_a_calm_afternoon_asks_nothing_special():
    conditions = Conditions.from_weather(a_weather(), AFTERNOON)

    assert conditions == Conditions() and conditions.guidance(Language.ES) == "" and not conditions.needs_calm_walk


def test_the_last_half_hour_of_light_already_counts_as_dark():
    almost_dark = datetime(2026, 10, 9, 17, 20, tzinfo=timezone.utc)  # 19:20 in Madrid

    assert Conditions.from_weather(a_weather(), almost_dark).dark


def test_rain_cold_and_wind_are_recognised():
    assert Conditions.from_weather(a_weather(sky=Sky.RAIN), AFTERNOON).rain
    assert Conditions.from_weather(a_weather(rain_mm=1.2), AFTERNOON).rain
    assert Conditions.from_weather(a_weather(temperature_c=2), AFTERNOON).cold
    assert Conditions.from_weather(a_weather(wind_kmh=50), AFTERNOON).windy
    assert Conditions.from_weather(a_weather(sky=Sky.STORM), AFTERNOON).storm


def test_the_conditions_survive_being_saved_as_text():
    conditions = Conditions(dark=True, rain=True)

    assert conditions.to_text() == "dark,rain" and Conditions.from_text("dark,rain") == conditions
    assert Conditions.from_text("") == Conditions()


def test_the_guidance_for_the_model_speaks_the_language_of_the_prompt():
    conditions = Conditions(dark=True)

    assert "calles con luz" in conditions.guidance(Language.ES)
    assert "lit" in conditions.guidance(Language.EN)


# --- starting a walk ---

def _start(weather_service, latitude=40.4, longitude=-3.7, now=AFTERNOON, generator=None):
    walks, generator = InMemoryWalkRepository(), generator or StubChallengeGenerator([a_challenge() for _ in range(3)])
    walk_id = uuid4()
    StartWalkCommandHandler(walks, generator, weather_service).handle(
        StartWalkCommand(walk_id=walk_id, user_id="u", mood=Mood.CALM, minutes=15, weather="sunny", challenges_count=3, latitude=latitude, longitude=longitude, now=now)
    )
    return walks.find_or_fail_by_id(walk_id), generator


def test_a_walk_at_night_is_careful_and_remembers_it():
    walk, generator = _start(FakeWeatherService(a_weather()), now=NIGHT)

    assert walk.conditions == "dark" and generator.briefs[0].conditions.dark


def test_a_calm_afternoon_changes_nothing():
    walk, generator = _start(FakeWeatherService(a_weather()))

    assert walk.conditions == "" and generator.briefs[0].conditions == Conditions()


def test_without_a_place_the_weather_is_not_asked():
    weather = FakeWeatherService(a_weather())

    walk, _ = _start(weather, latitude=None, longitude=None)

    assert weather.asked == [] and walk.conditions == ""


def test_if_the_weather_fails_the_walk_starts_anyway():
    walk, _ = _start(FakeWeatherService(fail=True))

    assert walk.conditions == "" and len(walk.challenges) == 3


def test_at_night_the_template_challenges_stay_on_lit_streets():
    generator = TemplateChallengeGenerator()

    walk, _ = _start(FakeWeatherService(a_weather()), now=NIGHT, generator=generator)

    calm_texts = {text for texts in CALM_TEXTS[Language.ES].values() for text in texts}
    assert all(challenge.text in calm_texts for challenge in walk.challenges)


def test_in_daylight_the_template_challenges_are_the_usual_ones():
    walk, _ = _start(FakeWeatherService(a_weather()), generator=TemplateChallengeGenerator())

    assert all(challenge.text in {text for texts in CHALLENGE_TEXTS[Language.ES].values() for text in texts} for challenge in walk.challenges)


def test_every_calm_challenge_exists_in_both_languages_for_each_category():
    for language in Language:
        assert all(len(texts) >= 2 for texts in CALM_TEXTS[language].values()) and len(CALM_TEXTS[language]) == 5


def test_a_swap_in_a_walk_at_night_stays_careful():
    walk = a_walk(conditions="dark,rain", challenges=[a_challenge()])
    repository = InMemoryWalkRepository()
    repository.save(walk)
    generator = StubChallengeGenerator([a_challenge()])

    SwapChallengeCommandHandler(repository, generator).handle(SwapChallengeCommand(walk_id=walk.id, challenge_id=walk.challenges[0].id))

    assert generator.briefs[0].conditions == Conditions(dark=True, rain=True)


# --- the context the app shows before the walk ---

def test_the_context_tells_the_weather_the_light_and_the_conditions():
    handler = FindWalkContextQueryHandler(FakeWeatherService(a_weather(sky=Sky.RAIN, temperature_c=11)))

    context = handler.handle(FindWalkContextQuery(latitude=40.4, longitude=-3.7, now=AFTERNOON))

    assert (context.temperature_c, context.sky, context.minutes_of_light) == (11, Sky.RAIN, 102)
    assert context.conditions.rain and context.suggested_weather == "rainy"


def test_the_suggested_weather_follows_the_sky():
    for sky, expected in ((Sky.CLEAR, "sunny"), (Sky.CLOUDY, "cloudy"), (Sky.FOG, "cloudy")):
        context = FindWalkContextQueryHandler(FakeWeatherService(a_weather(sky=sky))).handle(FindWalkContextQuery(40.4, -3.7, AFTERNOON))
        assert context.suggested_weather == expected
