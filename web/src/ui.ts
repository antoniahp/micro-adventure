// Names, colours and icons for what the backend sends as codes ("people_watching").
import type { IconName } from "./components/Icon";

export const CATEGORIES: Record<string, { label: string; icon: IconName; color: string; tint: string; ink: string }> = {
  sensory: { label: "Tacto", icon: "hand", color: "#F25C54", tint: "#FDECEA", ink: "#B6342D" },
  sound: { label: "Escucha", icon: "sound", color: "#2E8BEA", tint: "#E6F1FD", ink: "#1B63B3" },
  culture: { label: "Ciudad y cultura", icon: "landmark", color: "#7357E8", tint: "#EEEAFD", ink: "#5237C4" },
  nature: { label: "Naturaleza", icon: "leaf", color: "#10A878", tint: "#E2F6EF", ink: "#0A7656" },
  people_watching: { label: "Gente", icon: "eye", color: "#FFB300", tint: "#FFF4D6", ink: "#8A6100" },
};

export const FALLBACK_CATEGORY = { label: "Reto", icon: "star" as IconName, color: "#10A878", tint: "#E2F6EF", ink: "#0A7656" };

// Energy level, sent to the backend as a mood.
export const ENERGIES = [
  { value: "tired", label: "Baja" },
  { value: "calm", label: "Media" },
  { value: "active", label: "Alta" },
] as const;

export const MINUTES = [15, 30, 45, 60];

export const WEATHERS: { value: string; label: string; icon: IconName }[] = [
  { value: "sunny", label: "Sol", icon: "sun" },
  { value: "cloudy", label: "Nublado", icon: "cloud" },
  { value: "rainy", label: "Lluvia", icon: "rain" },
];

// Badges the backend can award. `hint` tells the player how to get the locked ones.
export const BADGES: { code: string; name: string; icon: IconName; color: string; hint: string }[] = [
  { code: "first_walk", name: "Primer paseo", icon: "pin", color: "#10A878", hint: "Completa un reto" },
  { code: "perfect_walk", name: "Paseo perfecto", icon: "star", color: "#FFB300", hint: "Completa todos los retos de un paseo sin cambiar ninguno" },
];
