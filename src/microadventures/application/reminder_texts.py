"""What the bot says. Spanish and English, like the rest of the app."""

from microadventures.domain.models.language import Language

TEXTS = {
    Language.ES: {
        "weekday": "🌿 Has terminado por hoy. Sal a caminar unos minutos y haz un reto: {url}",
        "weekend": "🌿 Buen momento para salir un rato. Te espera un paseo con retos: {url}",
        "linked": "✅ Conectado. Te avisaré a las {weekday} entre semana y a las {weekend} en fin de semana. "
        "Puedes cambiarlo en la app. Para dejar de recibir avisos escribe /stop.",
        "schedule_saved": "⏰ Listo. Te avisaré a las {weekday} entre semana y a las {weekend} en fin de semana.",
        "schedule_paused": "🔕 Avisos desactivados. Puedes volver a activarlos en la app.",
        "stopped": "Hecho, no te escribiré más. Puedes volver a conectarme desde la app.",
        "unknown_code": "Ese código ya no vale. Abre MicroAdventures, entra en Avisos y pulsa «Conectar Telegram».",
        "help": "Soy el aviso de MicroAdventures. Para conectarme abre la app, entra en Avisos y pulsa «Conectar Telegram».",
    },
    Language.EN: {
        "weekday": "🌿 You're done for today. Go for a few minutes' walk and do a challenge: {url}",
        "weekend": "🌿 A good moment to head out. A walk with challenges is waiting: {url}",
        "linked": "✅ Connected. I'll remind you at {weekday} on weekdays and at {weekend} on weekends. "
        "You can change it in the app. Send /stop to stop the reminders.",
        "schedule_saved": "⏰ Done. I'll remind you at {weekday} on weekdays and at {weekend} on weekends.",
        "schedule_paused": "🔕 Reminders are off. You can turn them back on in the app.",
        "stopped": "Done, I won't write to you again. You can connect me again from the app.",
        "unknown_code": "That code is no longer valid. Open MicroAdventures, go to Reminders and tap “Connect Telegram”.",
        "help": "I'm the MicroAdventures reminder. To connect me, open the app, go to Reminders and tap “Connect Telegram”.",
    },
}


def text(language: str, key: str, **values) -> str:
    texts = TEXTS.get(Language(language), TEXTS[Language.ES])
    return texts[key].format(**values)


def both_languages(key: str) -> str:
    """For a person we cannot tell the language of (they have not linked yet)."""
    return f"{text(Language.ES, key)}\n\n{text(Language.EN, key)}"


# --- The reminder card: a picture, a few lines and three buttons ---

CARD_TEXTS = {
    Language.ES: {
        "weekday_title": "🌿 <b>Tu jornada ha terminado.</b>",
        "weekend_title": "☀️ <b>Buena hora para salir.</b>",
        "weekday_invite": "Un paseo corto con retos te sienta bien.",
        "weekend_invite": "Unos minutos fuera y vuelves con una historia.",
        "light": "Quedan <b>{light}</b> de luz · {temperature} °C, {sky}.",
        "dark": "Ya es de noche · {temperature} °C, {sky}. Mejor un paseo corto por calles con luz.",
        "rain": "Llueve: hay retos para hacer bajo cubierto.",
        "open": "🚶 Salir a caminar",
        "snooze": "⏰ En 1 hora",
        "skip": "😴 Hoy no",
        "snoozed": "Vale, te aviso en 1 hora ⏰",
        "skipped": "Hecho, hoy no te molesto más 😴",
        "sky_clear": "despejado", "sky_cloudy": "nublado", "sky_fog": "niebla", "sky_rain": "lluvia", "sky_snow": "nieve", "sky_storm": "tormenta",
    },
    Language.EN: {
        "weekday_title": "🌿 <b>You're done for today.</b>",
        "weekend_title": "☀️ <b>A good time to head out.</b>",
        "weekday_invite": "A short walk with challenges will do you good.",
        "weekend_invite": "A few minutes outside and you come back with a story.",
        "light": "<b>{light}</b> of daylight left · {temperature} °C, {sky}.",
        "dark": "It is dark already · {temperature} °C, {sky}. Better a short walk along lit streets.",
        "rain": "It is raining: there are challenges to do under cover.",
        "open": "🚶 Go for a walk",
        "snooze": "⏰ In 1 hour",
        "skip": "😴 Not today",
        "snoozed": "Okay, I'll remind you in 1 hour ⏰",
        "skipped": "Done, I won't bother you again today 😴",
        "sky_clear": "clear", "sky_cloudy": "cloudy", "sky_fog": "fog", "sky_rain": "rain", "sky_snow": "snow", "sky_storm": "storm",
    },
}


def card_text(language: str, key: str, **values) -> str:
    texts = CARD_TEXTS.get(Language(language), CARD_TEXTS[Language.ES])
    return texts[key].format(**values)


def format_light(minutes: int, language: str) -> str:
    hours, rest = divmod(minutes, 60)
    if not hours:
        return f"{rest} min"
    return f"{hours} h {rest} min" if rest else f"{hours} h"
