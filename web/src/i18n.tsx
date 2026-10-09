// Spanish and English texts. Every word the person reads lives here, so adding a language
// means adding one more block below (and one more entry in LANGUAGES).
import { createContext, useCallback, useContext, useEffect, useMemo, useState, type ReactNode } from "react";

export type Lang = "es" | "en";
export const LANGUAGES: Lang[] = ["es", "en"];

const ES = {
  "app.tabWalk": "Paseo",
  "app.tabNotebook": "Cuaderno",
  "app.language": "Idioma",

  "start.hero": "Sal a caminar un rato antes de volver a casa.",
  "start.loading": "Preparando tu paseo",
  "start.noteLabel": "Cuéntame cómo vienes",
  "start.notePlaceholder": "Día de reuniones, necesito desconectar. Me apetece algo tranquilo, sin mucha gente.",
  "start.noteHint": "Gemma lee lo que escribas para elegir tus retos.",
  "start.time": "Tiempo",
  "start.energy": "Energía",
  "start.weather": "Clima",
  "start.submit": "Preparar mi paseo",
  "start.minutes": "{n} min",
  "start.count": "Retos",
  "start.countShort": "{n} retos sencillos, para ir sin prisa",
  "start.countFixed": "{n} retos para este rato",
  "start.countChoose": "Con más de una hora, tú eliges cuántos",

  "energy.tired": "Baja",
  "energy.calm": "Media",
  "energy.active": "Alta",
  "weather.sunny": "Sol",
  "weather.cloudy": "Nublado",
  "weather.rainy": "Lluvia",

  "cat.sensory": "Tacto",
  "cat.sound": "Escucha",
  "cat.culture": "Ciudad y cultura",
  "cat.nature": "Naturaleza",
  "cat.people_watching": "Gente",
  "cat.fallback": "Reto",

  "loader.1": "Buscando algo que tocar…",
  "loader.2": "Afinando el oído…",
  "loader.3": "Eligiendo un rincón con historia…",
  "loader.4": "Preparando tu cuaderno…",

  "walk.opening": "Abriendo tu paseo",
  "walk.title": "Tus retos de hoy",
  "walk.progress": "{done} de {total}",
  "walk.startAnother": "Empezar otro paseo",
  "walk.finishedTitle": "Paseo completado",
  "walk.finishedPerfect": "Sin cambiar ningún reto: paseo perfecto.",
  "walk.finishedNormal": "Has salido y lo has hecho. Eso ya cuenta.",
  "walk.seeNotebook": "Ver mi cuaderno",
  "walk.newWalk": "Nuevo paseo",
  "walk.noPeoplePhotos": "A la gente no se la fotografía: cuéntalo.",
  "walk.tell": "Contarlo",
  "walk.photo": "Foto",
  "walk.photoChecking": "Mirando tu foto…",
  "walk.photoAgain": "Otra foto",
  "walk.photoAlt": "Tu foto de este reto",
  "walk.sourceModel": "Escrito por {model}",
  "walk.sourceTemplate": "Reto de reserva (sin modelo)",
  "walk.swap": "Cambiar ({n})",
  "walk.noSwaps": "Sin cambios",
  "walk.swapWarning": "Si cambias un reto, el paseo ya no cuenta como perfecto.",
  "walk.finish": "Terminar paseo",
  "walk.endedTitle": "Paseo terminado",
  "walk.tellWalk": "Contar mi paseo",
  "walk.editTold": "Editar mi relato",
  "walk.backToChallenges": "Ver mis retos",
  "walk.seeSummary": "Ver el resumen del paseo",

  "finish.title": "Cuenta tu paseo",
  "finish.intro": "Todo es opcional. Es tu cuaderno.",
  "finish.minutes": "Minutos caminados",
  "finish.km": "Kilómetros",
  "finish.diary": "Tu paseo, con tus palabras",
  "finish.diaryPlaceholder": "Qué has visto, cómo vuelves, qué te llevas…",
  "finish.save": "Guardar mi paseo",
  "finish.later": "Ahora no",
  "finish.leave": "Salir sin contarlo",
  "done.challenges": "retos",
  "done.minutes": "minutos",
  "done.km": "km",
  "done.storyPrompt": "¿Quieres contar cómo ha ido? Con un par de líneas basta.",

  "story.aria": "Tu respuesta",
  "story.placeholder": "Cuéntalo con tus palabras: qué has visto, tocado, oído o pensado.",
  "story.transcribing": "Pasando tu voz a texto…",
  "story.record": "Grabar voz",
  "story.stop": "Parar ({n}s)",
  "story.send": "Enviar",
  "story.saving": "Guardando…",
  "story.cancel": "Cancelar",
  "story.minChars": "Escribe al menos {n} caracteres.",
  "story.micError": "No he podido usar el micrófono. Revisa el permiso del navegador o escríbelo.",

  "notebook.opening": "Abriendo tu cuaderno…",
  "notebook.title": "Tu cuaderno",
  "notebook.walks": "paseos",
  "notebook.days": "días fuera",
  "notebook.challenges": "retos",
  "notebook.badges": "Insignias",
  "notebook.empty": "Todavía no tienes ningún paseo. Las insignias aparecen al completar tus primeros retos.",
  "notebook.start": "Empezar un paseo",
  "badge.first_walk.name": "Primer paseo",
  "badge.first_walk.hint": "Completa un reto",
  "badge.perfect_walk.name": "Paseo perfecto",
  "badge.perfect_walk.hint": "Completa todos los retos de un paseo sin cambiar ninguno",

  "error.generic": "Algo ha fallado. Inténtalo de nuevo.",
  "error.notFound": "No encuentro ese paseo. Empieza uno nuevo.",
  "error.conflict": "Ese reto ya no se puede cambiar.",
  "error.rejected": "No he podido dar el reto por bueno. Cuéntalo con tus palabras o prueba otra foto.",
  "error.modelDown": "El guía está tardando más de lo normal. Inténtalo de nuevo en un momento.",
  "error.voiceOff": "La voz no está activada todavía. Escríbelo, por favor.",
  "error.voiceFailed": "No he podido entender el audio. Prueba otra vez o escríbelo.",
} as const;

export type TextKey = keyof typeof ES;

const EN: Record<TextKey, string> = {
  "app.tabWalk": "Walk",
  "app.tabNotebook": "Notebook",
  "app.language": "Language",

  "start.hero": "Go for a walk before heading home.",
  "start.loading": "Getting your walk ready",
  "start.noteLabel": "Tell me how you're arriving",
  "start.notePlaceholder": "Meeting-heavy day, I need to unwind. Something quiet, without many people.",
  "start.noteHint": "Gemma reads what you write to choose your challenges.",
  "start.time": "Time",
  "start.energy": "Energy",
  "start.weather": "Weather",
  "start.submit": "Get my walk ready",
  "start.minutes": "{n} min",
  "start.count": "Challenges",
  "start.countShort": "{n} simple challenges, no rush",
  "start.countFixed": "{n} challenges for this time",
  "start.countChoose": "With over an hour, you choose how many",

  "energy.tired": "Low",
  "energy.calm": "Medium",
  "energy.active": "High",
  "weather.sunny": "Sunny",
  "weather.cloudy": "Cloudy",
  "weather.rainy": "Rain",

  "cat.sensory": "Touch",
  "cat.sound": "Listen",
  "cat.culture": "City and culture",
  "cat.nature": "Nature",
  "cat.people_watching": "People",
  "cat.fallback": "Challenge",

  "loader.1": "Looking for something to touch…",
  "loader.2": "Tuning your ears…",
  "loader.3": "Picking a corner with a story…",
  "loader.4": "Preparing your notebook…",

  "walk.opening": "Opening your walk",
  "walk.title": "Today's challenges",
  "walk.progress": "{done} of {total}",
  "walk.startAnother": "Start another walk",
  "walk.finishedTitle": "Walk complete",
  "walk.finishedPerfect": "Not a single challenge swapped: perfect walk.",
  "walk.finishedNormal": "You went out and did it. That already counts.",
  "walk.seeNotebook": "See my notebook",
  "walk.newWalk": "New walk",
  "walk.noPeoplePhotos": "We don't photograph people: tell it instead.",
  "walk.tell": "Tell it",
  "walk.photo": "Photo",
  "walk.photoChecking": "Looking at your photo…",
  "walk.photoAgain": "Another photo",
  "walk.photoAlt": "Your photo for this challenge",
  "walk.sourceModel": "Written by {model}",
  "walk.sourceTemplate": "Fallback challenge (no model)",
  "walk.swap": "Swap ({n})",
  "walk.noSwaps": "No swaps left",
  "walk.swapWarning": "If you swap a challenge, the walk no longer counts as perfect.",
  "walk.finish": "End walk",
  "walk.endedTitle": "Walk ended",
  "walk.tellWalk": "Tell my walk",
  "walk.editTold": "Edit my story",
  "walk.backToChallenges": "See my challenges",
  "walk.seeSummary": "See the walk summary",

  "finish.title": "Tell your walk",
  "finish.intro": "Everything is optional. It's your notebook.",
  "finish.minutes": "Minutes walked",
  "finish.km": "Kilometres",
  "finish.diary": "Your walk, in your own words",
  "finish.diaryPlaceholder": "What you saw, how you're heading back, what you take with you…",
  "finish.save": "Save my walk",
  "finish.later": "Not now",
  "finish.leave": "Leave without telling it",
  "done.challenges": "challenges",
  "done.minutes": "minutes",
  "done.km": "km",
  "done.storyPrompt": "Want to tell how it went? A couple of lines is enough.",

  "story.aria": "Your answer",
  "story.placeholder": "Tell it in your own words: what you saw, touched, heard or thought.",
  "story.transcribing": "Turning your voice into text…",
  "story.record": "Record voice",
  "story.stop": "Stop ({n}s)",
  "story.send": "Send",
  "story.saving": "Saving…",
  "story.cancel": "Cancel",
  "story.minChars": "Write at least {n} characters.",
  "story.micError": "I couldn't use the microphone. Check the browser permission or write it instead.",

  "notebook.opening": "Opening your notebook…",
  "notebook.title": "Your notebook",
  "notebook.walks": "walks",
  "notebook.days": "days out",
  "notebook.challenges": "challenges",
  "notebook.badges": "Badges",
  "notebook.empty": "You have no walks yet. Badges appear when you complete your first challenges.",
  "notebook.start": "Start a walk",
  "badge.first_walk.name": "First walk",
  "badge.first_walk.hint": "Complete a challenge",
  "badge.perfect_walk.name": "Perfect walk",
  "badge.perfect_walk.hint": "Complete every challenge in a walk without swapping any",

  "error.generic": "Something went wrong. Please try again.",
  "error.notFound": "I can't find that walk. Start a new one.",
  "error.conflict": "That challenge can't be swapped any more.",
  "error.rejected": "I couldn't accept that one. Tell it in your own words or try another photo.",
  "error.modelDown": "The guide is taking longer than usual. Try again in a moment.",
  "error.voiceOff": "Voice isn't switched on yet. Please write it.",
  "error.voiceFailed": "I couldn't understand the audio. Try again or write it.",
};

const TEXTS: Record<Lang, Record<TextKey, string>> = { es: ES, en: EN };

const STORAGE_KEY = "lang";

// First visit: use the browser's language. After that: whatever the person chose.
function detectLanguage(): Lang {
  try {
    const saved = localStorage.getItem(STORAGE_KEY);
    if (saved === "es" || saved === "en") return saved;
  } catch {
    /* storage blocked: fall through */
  }
  return navigator.language?.toLowerCase().startsWith("es") ? "es" : "en";
}

// Plain-code access (api.ts is not a component, so it cannot use the hook).
let current: Lang = detectLanguage();

export function currentLanguage(): Lang {
  return current;
}

export function translate(key: TextKey, vars: Record<string, string | number> = {}, lang: Lang = current): string {
  return TEXTS[lang][key].replace(/\{(\w+)\}/g, (_, name) => String(vars[name] ?? ""));
}

type I18n = { lang: Lang; setLang: (lang: Lang) => void; t: (key: TextKey, vars?: Record<string, string | number>) => string };
const I18nContext = createContext<I18n | null>(null);

export function I18nProvider({ children }: { children: ReactNode }) {
  const [lang, setLangState] = useState<Lang>(current);

  const setLang = useCallback((next: Lang) => {
    current = next;
    setLangState(next);
    try {
      localStorage.setItem(STORAGE_KEY, next);
    } catch {
      /* the choice just won't be remembered */
    }
  }, []);

  // Screen readers and the browser's own translator need to know the page language.
  useEffect(() => {
    document.documentElement.lang = lang;
  }, [lang]);

  const value = useMemo<I18n>(() => ({ lang, setLang, t: (key, vars) => translate(key, vars, lang) }), [lang, setLang]);
  return <I18nContext.Provider value={value}>{children}</I18nContext.Provider>;
}

export function useI18n(): I18n {
  const value = useContext(I18nContext);
  if (!value) throw new Error("useI18n must be used inside <I18nProvider>");
  return value;
}
