import { useEffect, useState } from "react";
import { getProgress } from "../api";
import Icon from "../components/Icon";
import { getUserId } from "../storage";
import type { Progress } from "../types";
import { BADGES } from "../ui";

export default function NotebookScreen({ onStartWalk }: { onStartWalk: () => void }) {
  const [progress, setProgress] = useState<Progress | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    getProgress(getUserId()).then(setProgress).catch((e: Error) => setError(e.message));
  }, []);

  if (error) return <p className="error" role="alert">{error}</p>;
  if (!progress) return <p className="hint">Abriendo tu cuaderno…</p>;

  return (
    <section>
      <h2>Tu cuaderno</h2>

      <dl className="stats">
        <div style={{ "--n": "#F25C54" } as React.CSSProperties}><dd>{progress.walks_count}</dd><dt>paseos</dt></div>
        <div style={{ "--n": "#2E8BEA" } as React.CSSProperties}><dd>{progress.days_walked}</dd><dt>días fuera</dt></div>
        <div style={{ "--n": "#10A878" } as React.CSSProperties}><dd>{progress.challenges_completed}</dd><dt>retos</dt></div>
      </dl>

      <h3>Insignias</h3>
      <ul className="badges">
        {BADGES.map((b) => {
          const earned = progress.stickers.includes(b.code);
          return (
            <li key={b.code} className={earned ? "pin earned" : "pin"} style={{ "--c": b.color, "--on": b.color === "#FFB300" ? "#1d1b3a" : "#fff" } as React.CSSProperties}>
              <span className="pin-icon"><Icon name={earned ? b.icon : "lock"} size={30} /></span>
              <strong>{b.name}</strong>
              {!earned && <small>{b.hint}</small>}
            </li>
          );
        })}
      </ul>

      {progress.walks_count === 0 && (
        <>
          <p className="hint">Todavía no tienes ningún paseo. Las insignias aparecen al completar tus primeros retos.</p>
          <button className="btn btn-primary" onClick={onStartWalk}>Empezar un paseo</button>
        </>
      )}
    </section>
  );
}
