import { useEffect, useState, type CSSProperties } from "react";
import { getProgress } from "../api";
import Icon from "../components/Icon";
import { useI18n, type TextKey } from "../i18n";
import { getUserId } from "../storage";
import type { Progress } from "../types";
import { STICKERS } from "../ui";

const UNITS: Record<string, string> = { ten_km: " km", five_hours: " min" };

// The notebook: one page with every sticker. The earned ones are stuck on; the others show their goal and how far you are.
export default function NotebookScreen({ onStartWalk }: { onStartWalk: () => void }) {
  const { t } = useI18n();
  const [progress, setProgress] = useState<Progress | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    getProgress(getUserId()).then(setProgress).catch((e: Error) => setError(e.message));
  }, []);

  if (error) return <p className="error" role="alert">{error}</p>;
  if (!progress) return <p className="hint">{t("notebook.opening")}</p>;

  const earned = progress.sticker_book.filter((s) => s.unlocked).length;
  const streak = progress.current_streak;

  return (
    <section>
      <h2>{t("notebook.title")}</h2>

      <div className="notebook-head">
        <strong>{t("notebook.earned", { done: earned, total: progress.sticker_book.length })}</strong>
        {streak > 0 && (
          <span className="streak"><Icon name="flame" size={18} /> {streak === 1 ? t("notebook.streakOne") : t("notebook.streak", { n: streak })}</span>
        )}
      </div>
      <p className="hint">{t("notebook.page")}</p>

      <ul className="page">
        {progress.sticker_book.map((sticker) => {
          const look = STICKERS[sticker.code] ?? { icon: "star", color: "#10A878" };
          const unit = UNITS[sticker.code] ?? "";
          const share = Math.round((sticker.current / sticker.goal) * 100);
          return (
            <li
              key={sticker.code}
              className={sticker.unlocked ? "sticker earned" : "sticker"}
              style={{ "--c": look.color, "--p": `${share}%`, "--on": look.color === "#FFB300" ? "#1d1b3a" : "#fff" } as CSSProperties}
            >
              <span className="sticker-art"><Icon name={sticker.unlocked ? look.icon : "lock"} size={30} /></span>
              <strong>{t(`sticker.${sticker.code}.name` as TextKey)}</strong>
              {sticker.unlocked ? (
                <small className="ok-line"><Icon name="check" size={14} /> {t(`sticker.${sticker.code}.goal` as TextKey)}</small>
              ) : (
                <>
                  <small>{t(`sticker.${sticker.code}.goal` as TextKey)}</small>
                  <span className="meter" role="img" aria-label={`${sticker.current}${unit} / ${sticker.goal}${unit}`}><i /></span>
                  <small className="count">{t("notebook.goal", { current: `${sticker.current}${unit}`, goal: `${sticker.goal}${unit}` })}</small>
                </>
              )}
            </li>
          );
        })}
      </ul>

      {progress.walks_count === 0 && (
        <>
          <p className="hint">{t("notebook.empty")}</p>
          <button className="btn btn-primary" onClick={onStartWalk}>{t("notebook.start")}</button>
        </>
      )}
    </section>
  );
}
