import { useEffect, useState, type CSSProperties } from "react";
import { getProgress } from "../api";
import Icon from "../components/Icon";
import { hasText, useI18n, type TextKey } from "../i18n";
import { getUserId } from "../storage";
import type { Progress } from "../types";
import { stickerWords, type Sticker } from "../components/stickerWords";
import { CATEGORIES, LIGHT_STICKER_COLORS, STICKER_FAMILIES, STICKER_ICONS } from "../ui";

const UNITS: Record<string, string> = { km: " km" };

// Time goals are named in hours ("5 hours outdoors"), so their progress reads in hours too: "1 h 25 min of 5 h".
function amount(family: string, value: number): string {
  const text = family !== "minutes" ? `${value}${UNITS[family] ?? ""}` : hoursAndMinutes(value);
  return text.replace(/ /g, "\u00a0"); // one amount never splits across lines: "1 h 25 min" stays together
}

function hoursAndMinutes(value: number): string {
  const hours = Math.floor(value / 60);
  const minutes = value % 60;
  if (hours === 0) return `${minutes} min`;
  return minutes === 0 ? `${hours} h` : `${hours} h ${minutes} min`;
}


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

  const words = (sticker: Sticker, level: number) => stickerWords(t, sticker, level);

  // The notebook is read by theme: walks, challenges, streaks... each with its own stickers, from the first to the hardest.
  const groups: { family: string; stickers: Sticker[] }[] = [];
  for (const sticker of progress.sticker_book) {
    const group = groups.find((g) => g.family === sticker.family);
    if (group) group.stickers.push(sticker);
    else groups.push({ family: sticker.family, stickers: [sticker] });
  }

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

      {groups.map((group) => {
        const done = group.stickers.filter((s) => s.unlocked).length;
        const title = group.family in CATEGORIES ? t(`cat.${group.family}` as TextKey) : t(`sticker.group.${group.family}` as TextKey);
        return (
          <div key={group.family} className="sticker-group">
            <h3 className="sticker-group-title">
              {title} <small>{t("sticker.group.count", { done, total: group.stickers.length })}</small>
            </h3>
            <ul className="page">
              {group.stickers.map((sticker, level) => {
                const family = STICKER_FAMILIES[sticker.family] ?? { icon: "star" as const, color: "#10A878" };
                const look = { icon: STICKER_ICONS[sticker.code] ?? family.icon, color: family.color };
                const current = amount(sticker.family, sticker.current);
                const target = amount(sticker.family, sticker.goal);
                const share = Math.round((sticker.current / sticker.goal) * 100);
                const { name, goal, explain } = words(sticker, level);
                return (
                  <li
                    key={sticker.code}
                    title={goal}
                    className={sticker.unlocked ? "sticker earned" : "sticker"}
                    style={{ "--c": look.color, "--p": `${share}%`, "--on": LIGHT_STICKER_COLORS.has(look.color) ? "#1d1b3a" : "#fff" } as CSSProperties}
                  >
                    <span className="sticker-art"><Icon name={sticker.unlocked ? look.icon : "lock"} size={30} /></span>
                    <strong>{name}</strong>
                    {sticker.unlocked ? (
                      explain && <small className="ok-line"><Icon name="check" size={14} /> {goal}</small>
                    ) : (
                      <>
                        {explain && <small>{goal}</small>}
                        <span className="meter" role="img" aria-label={`${current} / ${target}`}><i /></span>
                        <small className="count">{t("notebook.goal", { current, goal: target })}</small>
                      </>
                    )}
                  </li>
                );
              })}
            </ul>
          </div>
        );
      })}

      {progress.walks_count === 0 && (
        <>
          <p className="hint">{t("notebook.empty")}</p>
          <button className="btn btn-primary" onClick={onStartWalk}>{t("notebook.start")}</button>
        </>
      )}
    </section>
  );
}
