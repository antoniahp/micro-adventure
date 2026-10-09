// Colours and icons for what the backend sends as codes ("people_watching").
// The words (names, hints) live in i18n.tsx: cat.<code>, energy.<value>, weather.<value>, badge.<code>.*
import type { IconName } from "./components/Icon";

export const CATEGORIES: Record<string, { icon: IconName; color: string; tint: string; ink: string }> = {
  sensory: { icon: "hand", color: "#F25C54", tint: "#FDECEA", ink: "#B6342D" },
  sound: { icon: "sound", color: "#2E8BEA", tint: "#E6F1FD", ink: "#1B63B3" },
  culture: { icon: "landmark", color: "#7357E8", tint: "#EEEAFD", ink: "#5237C4" },
  nature: { icon: "leaf", color: "#10A878", tint: "#E2F6EF", ink: "#0A7656" },
  people_watching: { icon: "eye", color: "#FFB300", tint: "#FFF4D6", ink: "#8A6100" },
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

// Badges the backend can award.
export const BADGES: { code: string; icon: IconName; color: string }[] = [
  { code: "first_walk", icon: "pin", color: "#10A878" },
  { code: "perfect_walk", icon: "star", color: "#FFB300" },
];
