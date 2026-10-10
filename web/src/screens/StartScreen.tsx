import { useEffect, useState } from "react";
import { getContext, startWalk, warmUp } from "../api";
import ContextCard, { type ContextState } from "../components/ContextCard";
import { getPlace, rememberedPlaceAllowed } from "../location";
import Trail from "../components/Trail";
import Icon from "../components/Icon";
import Loader from "../components/Loader";
import { useI18n, type TextKey } from "../i18n";
import { useSky } from "../sky";
import { getUserId } from "../storage";
import type { Mood, Place } from "../types";
import { challengeRange, ENERGIES, MINUTES, WEATHERS } from "../ui";

const MAX_NOTE = 500;

export default function StartScreen({ onStarted }: { onStarted: (walkId: string) => void }) {
  const { t } = useI18n();
  const sky = useSky();
  const [note, setNote] = useState("");
  const [mood, setMood] = useState<Mood>("calm");
  const [minutes, setMinutes] = useState(30);
  const [weather, setWeather] = useState("sunny");
  const [chosenCount, setChosenCount] = useState<number | null>(null); // only chosen when the walk is an hour or more
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [place, setPlace] = useState<Place | undefined>(undefined);
  const [context, setContext] = useState<ContextState>({ status: "idle" });

  // The model takes a few seconds to load. Starting it as soon as the form opens
  // means it is usually ready by the time the person has written their note.
  useEffect(() => {
    warmUp().catch(() => {}); // not essential: if it fails, the walk still starts
  }, []);

  // Where the person is decides the weather and the light, and these decide which challenges are safe.
  async function askContext() {
    setContext({ status: "loading" });
    try {
      const here = await getPlace();
      setPlace(here);
      const found = await getContext(here);
      setContext({ status: "ready", context: found });
      setWeather(found.suggested_weather);
    } catch (e) {
      setContext({ status: "failed", reason: (e as Error).message === "denied" ? "denied" : "unavailable" });
    }
  }

  useEffect(() => {
    if (rememberedPlaceAllowed()) void askContext(); // they already allowed it: no need to ask again
  }, []);

  const range = challengeRange(minutes);
  const canChoose = range.min !== range.max;
  const count = canChoose && chosenCount !== null && chosenCount >= range.min && chosenCount <= range.max ? chosenCount : range.usual;
  const counts = Array.from({ length: range.max - range.min + 1 }, (_, i) => range.min + i);

  async function submit() {
    setLoading(true);
    setError("");
    try {
      onStarted(await startWalk(getUserId(), mood, minutes, weather, note.trim(), count, place));
    } catch (e) {
      setError((e as Error).message);
      setLoading(false);
    }
  }

  if (loading) return <Loader title={t("start.loading")} />;

  return (
    <section className="start">
      <div className="hero-card" style={{ background: `linear-gradient(180deg, ${sky.top} 0%, ${sky.bottom} 100%)` }}>
        <h2 className="hero">{t("start.hero")}</h2>
        <Trail sky={sky} />
      </div>

      <ContextCard state={context} onAsk={askContext} />

      <div className="field">
        <label htmlFor="note">{t("start.noteLabel")}</label>
        <textarea
          id="note"
          rows={4}
          maxLength={MAX_NOTE}
          value={note}
          onChange={(e) => setNote(e.target.value)}
          placeholder={t("start.notePlaceholder")}
        />
        <p className="hint">
          {t("start.noteHint")} <span className="count">{note.length}/{MAX_NOTE}</span>
        </p>
      </div>

      <fieldset>
        <legend>{t("start.time")}</legend>
        <div className="segments">
          {MINUTES.map((m) => (
            <button key={m} className={minutes === m ? "segment selected" : "segment"} aria-pressed={minutes === m} onClick={() => setMinutes(m)}>
              {t("start.minutes", { n: m })}
            </button>
          ))}
        </div>
      </fieldset>

      <fieldset>
        <legend>{t("start.count")}</legend>
        {canChoose ? (
          <>
            <div className="segments counts">
              {counts.map((n) => (
                <button key={n} className={count === n ? "segment selected" : "segment"} aria-pressed={count === n} onClick={() => setChosenCount(n)}>
                  {n}
                </button>
              ))}
            </div>
            <p className="hint">{t("start.countChoose")}</p>
          </>
        ) : (
          <p className="hint count-line">{range.usual === 3 ? t("start.countShort", { n: count }) : t("start.countFixed", { n: count })}</p>
        )}
      </fieldset>

      <fieldset>
        <legend>{t("start.energy")}</legend>
        <div className="segments">
          {ENERGIES.map((e) => (
            <button key={e.value} className={mood === e.value ? "segment selected" : "segment"} aria-pressed={mood === e.value} onClick={() => setMood(e.value)}>
              {t(`energy.${e.value}` as TextKey)}
            </button>
          ))}
        </div>
      </fieldset>

      <fieldset>
        <legend>{t("start.weather")}</legend>
        <div className="segments">
          {WEATHERS.map((w) => (
            <button key={w.value} className={weather === w.value ? "segment selected" : "segment"} aria-pressed={weather === w.value} onClick={() => setWeather(w.value)}>
              <Icon name={w.icon} size={18} /> {t(`weather.${w.value}` as TextKey)}
            </button>
          ))}
        </div>
        <p className="hint">{t(context.status === "ready" ? "start.weatherAuto" : "start.weatherPick")}</p>
      </fieldset>

      {error && <p className="error" role="alert">{error}</p>}
      <button className="btn btn-primary btn-big" onClick={submit}>{t("start.submit")}</button>
    </section>
  );
}
