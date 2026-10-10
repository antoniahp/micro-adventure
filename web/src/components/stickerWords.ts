import { hasText, type TextKey } from "../i18n";
import type { Progress } from "../types";
import { CATEGORIES } from "../ui";

export type Sticker = Progress["sticker_book"][number];
const ROMAN = ["I", "II", "III", "IV", "V"];

type Translate = (key: TextKey, vars?: Record<string, string | number>) => string;

// The words of a sticker. A few keep their own name ("Primer paseo"); the rest are built from their family and goal.
// `level` is its position inside its family (0 for the first).
export function stickerWords(t: Translate, sticker: Sticker, level: number) {
  const own = `sticker.${sticker.code}`;
  if (hasText(`${own}.name`)) return { name: t(`${own}.name` as TextKey), goal: t(`${own}.goal` as TextKey), explain: true };
  if (sticker.family in CATEGORIES) {
    const category = t(`cat.${sticker.family}` as TextKey).toLowerCase();
    return {
      name: t("sticker.category.name", { name: t(`sticker.cat.${sticker.family}` as TextKey), level: ROMAN[level] ?? level + 1 }),
      goal: t("sticker.category.goal", { n: sticker.goal, category }),
      explain: true,
    };
  }
  const n = sticker.family === "minutes"
    ? (sticker.goal === 60 ? t("sticker.hour", { n: 1 }) : t("sticker.hours", { n: sticker.goal / 60 }))
    : sticker.goal;
  return { name: t(`sticker.${sticker.family}.name` as TextKey, { n }), goal: t(`sticker.${sticker.family}.goal` as TextKey, { n }), explain: false };
}
