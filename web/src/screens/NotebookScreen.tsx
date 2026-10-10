import { useEffect, useState, type CSSProperties } from "react";
import { getProgress } from "../api";
import Icon from "../components/Icon";
import { hasText, useI18n, type TextKey } from "../i18n";
import { getUserId } from "../storage";
import type { Progress } from "../types";
import { CATEGORIES, LIGHT_STICKER_COLORS, STICKER_FAMILIES, STICKER_ICONS } from "../ui";

const UNITS: Record<string, string> = { km: " km", minutes: " min" };
const ROMAN = ["I", "II", "III", "IV", "V"];

type Sticker = Progress["sticker_book"][number];

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

  // The words of a sticker. A few keep their own name ("Primer paseo"); the rest are built from their family and goal.
  function words(sticker: Sticker, level: number) {
    const own = `sticker.${sticker.code}`;
    if (hasText(`${own}.name`)) return { name: t(`${own}.name` as TextKey), goal: t(`${own}.goal` as TextKey), explain: true };
    const isCategory = sticker.family in CATEGORIES;
    if (isCategory) {
      const category = t(`cat.${sticker.family}` as TextKey).toLowerCase();
      return {
        name: t("sticker.category.name", { name: t(`sticker.cat.${sticker.family}` as TextKey), level: ROMAN[level] ?? level + 1 }),
        goal: t("sticker.category.goal", { n: sticker.goal, category }),
        explain: true,
      };
    }
    const n = sticker.family === "minutes" ? hours(sticker.goal) : sticker.goal;
    return { name: t(`sticker.${sticker.family}.name` as TextKey, { n }), goal: t(`sticker.${sticker.family}.goal` as TextKey, { n }), explain: false };
  }
  const hours = (minutes: number) => (minutes === 60 ? t("sticker.hour", { n: 1 }) : t("sticker.hours", { n: minutes / 60 }));

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
                const unit = UNITS[sticker.family] ?? "";
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
                        <span className="meter" role="img" aria-label={`${sticker.current}${unit} / ${sticker.goal}${unit}`}><i /></span>
                        <small className="count">{t("notebook.goal", { current: `${sticker.current}${unit}`, goal: `${sticker.goal}${unit}` })}</small>
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
