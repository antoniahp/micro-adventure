// Colours and icons for what the backend sends as codes ("people_watching").
// The words (names, hints) live in i18n.tsx: cat.<code>, energy.<value>, weather.<value>, badge.<code>.*
import type { IconName } from "./components/Icon";

export const CATEGORIES: Record<string, { icon: IconName; color: string; tint: string; ink: string }> = {
  sensory: { icon: "hand", color: "#A0522D", tint: "#FDECEA", ink: "#B6342D" },
  sound: { icon: "sound", color: "#3BB5F0", tint: "#E6F1FD", ink: "#1B63B3" },
  culture: { icon: "landmark", color: "#C050E0", tint: "#EEEAFD", ink: "#5237C4" },
  nature: { icon: "leaf", color: "#10A878", tint: "#E2F6EF", ink: "#0A7656" },
  people_watching: { icon: "eye", color: "#84B823", tint: "#FFF4D6", ink: "#8A6100" },
};

export const FALLBACK_CATEGORY = { icon: "star" as IconName, color: "#10A878", tint: "#E2F6EF", ink: "#0A7656" };

// Energy level, sent to the backend as a mood.
export const ENERGIES = [
  { value: "tired" },
  { value: "calm" },
  { value: "active" },
] as const;

export const MINUTES = [15, 30, 45, 60];

// How many challenges a walk can have for the time the person has. Same rule as the backend (WalkLength):
// under 45 minutes, 3 simple ones; 45 to 59, 5; an hour or more, from 6 to 10 and they choose.
export function challengeRange(minutes: number) {
  if (minutes < 45) return { min: 3, max: 3, usual: 3 };
  if (minutes < 60) return { min: 5, max: 5, usual: 5 };
  return { min: 6, max: 10, usual: 6 };
}

export const WEATHERS: { value: string; icon: IconName }[] = [
  { value: "sunny", icon: "sun" },
  { value: "cloudy", icon: "cloud" },
  { value: "rainy", icon: "rain" },
];

// The stickers of the notebook. The backend sends the code, the goal and how far the person is; the look is here.
export const STICKER_FAMILIES: Record<string, { icon: IconName; color: string }> = {
  walks: { icon: "compass", color: "#2E6FEA" },
  challenges: { icon: "check", color: "#F25C54" },
  perfect: { icon: "star", color: "#FFB300" },
  streak: { icon: "flame", color: "#FF7A45" },
  km: { icon: "route", color: "#0E9F9F" },
  minutes: { icon: "clock", color: "#5B5BD6" },
  stories: { icon: "chat", color: "#8B5CF6" },
  categories: { icon: "grid", color: "#E8579A" },
  // The five categories have their own colours here, apart from the ones of the challenge cards, so no sticker group repeats another.
  sensory: { icon: "hand", color: "#A0522D" },
  sound: { icon: "sound", color: "#3BB5F0" },
  culture: { icon: "landmark", color: "#C050E0" },
  nature: { icon: "leaf", color: "#10A878" },
  people_watching: { icon: "eye", color: "#84B823" },
};

// Colours that need dark ink on top: a white drawing would not read on them.
export const LIGHT_STICKER_COLORS = new Set(["#FFB300", "#84B823", "#3BB5F0", "#FF7A45"]);

// A few stickers keep their own icon (the first one is a pin, not a check); the colour always comes from the group.
export const STICKER_ICONS: Record<string, IconName> = {
  first_walk: "pin",
  all_categories: "grid",
};
