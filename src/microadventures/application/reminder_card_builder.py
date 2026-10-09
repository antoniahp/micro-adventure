from datetime import datetime

from microadventures.application.reminder_texts import card_text, format_light
from microadventures.domain.models.conditions import Conditions
from microadventures.domain.models.reminder_card import ReminderCard
from microadventures.domain.models.reminder_settings import ReminderSettings
from microadventures.domain.models.weather import Weather


def build_reminder_card(settings: ReminderSettings, weekend: bool, weather: Weather | None, now: datetime, app_url: str) -> ReminderCard:
    """The message of a reminder. With the weather it says the light that is left; without it, it still invites."""
    language = settings.language
    kind = "weekend" if weekend else "weekday"
    lines = [card_text(language, f"{kind}_title")]
    if weather is None:
        lines.append(card_text(language, f"{kind}_invite"))
    else:
        conditions = Conditions.from_weather(weather, now)
        values = {"temperature": round(weather.temperature_c), "sky": card_text(language, f"sky_{weather.sky.value}")}
        if conditions.dark:
            lines.append(card_text(language, "dark", **values))
        else:
            lines.append(card_text(language, "light", light=format_light(weather.minutes_of_light(now), language), **values))
        if conditions.rain and not conditions.dark:
            lines.append(card_text(language, "rain"))
    base = app_url.rstrip("/")
    return ReminderCard(
        photo_url=f"{base}/reminder-{kind}.png" if base else "",
        caption="\n\n".join(lines),
        open_label=card_text(language, "open"),
        open_url=base,
        snooze_label=card_text(language, "snooze"),
        skip_label=card_text(language, "skip"),
    )
