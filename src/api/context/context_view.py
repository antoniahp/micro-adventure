from datetime import datetime, timezone

from ninja import Query, Router

from api import wiring
from api.context.context_serializer import WalkContextOut
from microadventures.application.queries.find_walk_context.find_walk_context_query import FindWalkContextQuery

router = Router()  # mounted at /context


def _out(context) -> dict:
    return {
        "temperature_c": round(context.temperature_c, 1),
        "sky": context.sky.value,
        "rain_mm": context.rain_mm,
        "wind_kmh": round(context.wind_kmh),
        "sunrise": context.sunrise,
        "sunset": context.sunset,
        "minutes_of_light": context.minutes_of_light,
        "suggested_weather": context.suggested_weather,
        "conditions": {name: getattr(context.conditions, name) for name in context.conditions.__dataclass_fields__},
    }


@router.get("", response=WalkContextOut)
def get_context(request, latitude: float = Query(..., ge=-90, le=90), longitude: float = Query(..., ge=-180, le=180)):
    """The weather and the light where the person is. Nothing is stored."""
    query = FindWalkContextQuery(latitude=latitude, longitude=longitude, now=datetime.now(timezone.utc))
    return _out(wiring.find_walk_context_handler().handle(query))
