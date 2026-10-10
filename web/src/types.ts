// These types mirror the JSON that the Django API returns (see src/api/schemas.py).

export type Mood = "tired" | "calm" | "active";

export type Challenge = {
  id: string;
  category: string;
  text: string;
  status: "pending" | "completed";
  accepts_photo: boolean;
  story: string;
  source: string; // "template" or the model that wrote it, e.g. "gemma4:31b"
};

export type Walk = {
  id: string;
  user_id: string;
  mood: Mood;
  minutes: number;
  weather: string;
  note: string;
  language: string;
  swaps_used: number;
  walked_minutes: number | null;
  distance_km: number | null;
  diary: string;
  finished_at: string | null;
  created_at: string;
  challenges: Challenge[];
};

export type Progress = {
  walks_count: number;
  days_walked: number;
  challenges_completed: number;
  perfect_walks: number;
  stickers: string[];
  sticker_book: { code: string; family: string; current: number; goal: number; unlocked: boolean }[];
  current_streak: number;
};

export type WeeklySummary = {
  week_start: string;
  week_end: string;
  walks_count: number;
  days_walked: number;
  challenges_completed: number;
  perfect_walks: number;
  minutes: number;
  km: number;
  stories: number;
  days: { day: string; walks: number; challenges: number }[];
  moods: Record<string, number>;
  categories: Record<string, number>;
  previous_walks: number;
  previous_challenges: number;
  previous_minutes: number;
  previous_km: number;
  feeling: number | null;
  feeling_note: string;
};

export type YearlySummary = {
  year: number;
  years: number[];
  walks_count: number;
  days_walked: number;
  challenges_completed: number;
  perfect_walks: number;
  minutes: number;
  km: number;
  stories: number;
  longest_streak: number;
  best_month: number | null;
  months: { month: number; walks: number; challenges: number; minutes: number; km: number; feeling: number | null }[];
  moods: Record<string, number>;
  categories: Record<string, number>;
  weekdays: number[];
};

export type WalkContext = {
  temperature_c: number;
  sky: "clear" | "cloudy" | "fog" | "rain" | "snow" | "storm";
  rain_mm: number;
  wind_kmh: number;
  sunrise: string;
  sunset: string;
  minutes_of_light: number;
  suggested_weather: "sunny" | "cloudy" | "rainy";
  conditions: { dark: boolean; rain: boolean; storm: boolean; cold: boolean; hot: boolean; windy: boolean };
};

export type Place = { latitude: number; longitude: number };

export type Reminders = {
  enabled: boolean;
  weekday_time: string; // "18:00"
  weekend_time: string;
  timezone: string; // "Europe/Madrid"
  language: string;
  telegram_connected: boolean;
  has_place: boolean; // the reminder tells the weather where the person is
  telegram_available: boolean; // false when the server has no bot
};
