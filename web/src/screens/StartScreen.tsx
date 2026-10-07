import { useEffect, useState } from "react";
import { startWalk, warmUp } from "../api";
import Trail from "../components/Trail";
import Icon from "../components/Icon";
import Loader from "../components/Loader";
import { getUserId } from "../storage";
import type { Mood } from "../types";
import { ENERGIES, MINUTES, WEATHERS } from "../ui";

const MAX_NOTE = 500;

export default function StartScreen({ onStarted }: { onStarted: (walkId: string) => void }) {
  const [note, setNote] = useState("");
  const [mood, setMood] = useState<Mood>("calm");
  const [minutes, setMinutes] = useState(30);
  const [weather, setWeather] = useState("sunny");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  // The model takes a few seconds to load. Starting it as soon as the form opens
  // means it is usually ready by the time the person has written their note.
  useEffect(() => {
    warmUp().catch(() => {}); // not essential: if it fails, the walk still starts
  }, []);

  async function submit() {
    setLoading(true);
    setError("");
    try {
      onStarted(await startWalk(getUserId(), mood, minutes, weather, note.trim()));
    } catch (e) {
      setError((e as Error).message);
      setLoading(false);
    }
  }

  if (loading) return <Loader title="Preparando tu paseo" />;

  return (
    <section className="start">
      <div className="hero-card">
        <h2 className="hero">Sal a caminar un rato antes de volver a casa.</h2>
        <Trail />
      </div>

      <div className="field">
        <label htmlFor="note">Cuéntame cómo vienes</label>
        <textarea
          id="note"
          rows={4}
          maxLength={MAX_NOTE}
          value={note}
          onChange={(e) => setNote(e.target.value)}
          placeholder="Día de reuniones, necesito desconectar. Me apetece algo tranquilo, sin mucha gente."
        />
        <p className="hint">
          Gemma lee lo que escribas para elegir tus retos. <span className="count">{note.length}/{MAX_NOTE}</span>
        </p>
      </div>

      <fieldset>
        <legend>Tiempo</legend>
        <div className="segments">
          {MINUTES.map((m) => (
            <button key={m} className={minutes === m ? "segment selected" : "segment"} aria-pressed={minutes === m} onClick={() => setMinutes(m)}>
              {m} min
            </button>
          ))}
        </div>
      </fieldset>

      <fieldset>
        <legend>Energía</legend>
        <div className="segments">
          {ENERGIES.map((e) => (
            <button key={e.value} className={mood === e.value ? "segment selected" : "segment"} aria-pressed={mood === e.value} onClick={() => setMood(e.value)}>
              {e.label}
            </button>
          ))}
        </div>
      </fieldset>

      <fieldset>
        <legend>Clima</legend>
        <div className="segments">
          {WEATHERS.map((w) => (
            <button key={w.value} className={weather === w.value ? "segment selected" : "segment"} aria-pressed={weather === w.value} onClick={() => setWeather(w.value)}>
              <Icon name={w.icon} size={18} /> {w.label}
            </button>
          ))}
        </div>
      </fieldset>

      {error && <p className="error" role="alert">{error}</p>}
      <button className="btn btn-primary btn-big" onClick={submit}>Preparar mi paseo</button>
    </section>
  );
}
