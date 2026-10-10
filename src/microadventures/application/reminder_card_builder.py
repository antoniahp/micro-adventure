from datetime import datetime

from microadventures.application.reminder_texts import card_text, format_light
from microadventures.domain.models.conditions import Conditions
from microadventures.domain.models.reminder_card import ReminderCard
from microadventures.domain.models.reminder_settings import ReminderSettings, parse_timezone
from microadventures.domain.models.weather import Weather


def build_reminder_card(
    settings: ReminderSettings, weekend: bool, weather: Weather | None, now: datetime, app_url: str, nickname: str | None = None
) -> ReminderCard:
    """The message of a reminder. With the weather it says the light that is left; without it, it still invites.

    nickname is optional, like the field itself: without one the card reads exactly as it always has.
    """
    language = settings.language
    kind = "weekend" if weekend else "weekday"
    lines = []
    if nickname:
        lines.append(card_text(language, "greeting", nickname=nickname))
    lines.append(card_text(language, f"{kind}_title"))
    night = _is_night(settings, now)
    if weather is None:
        lines.append(card_text(language, f"{kind}_invite"))
    else:
        conditions = Conditions.from_weather(weather, now)
        values = {"temperature": round(weather.temperature_c), "sky": card_text(language, f"sky_{weather.sky.value}")}
        night = conditions.dark  # the sun knows better than the clock
        if conditions.dark:
            lines.append(card_text(language, "dark", **values))
        else:
            lines.append(card_text(language, "light", light=format_light(weather.minutes_of_light(now), language), **values))
        if conditions.rain and not conditions.dark:
            lines.append(card_text(language, "rain"))
    base = app_url.rstrip("/")
    return ReminderCard(
        photo_url=f"{base}/reminder-{'night' if night else kind}.png" if base else "",
        caption="\n\n".join(lines),
        open_label=card_text(language, "open"),
        open_url=base,
        snooze_label=card_text(language, "snooze"),
        skip_label=card_text(language, "skip"),
    )


def _is_night(settings: ReminderSettings, now: datetime) -> bool:
    """Without the weather there is no sunset to look at, so late evening and the small hours count as night."""
    return not (6 <= now.astimezone(parse_timezone(settings.timezone)).hour < 21)
