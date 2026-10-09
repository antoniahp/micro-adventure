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
