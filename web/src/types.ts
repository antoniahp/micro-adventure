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
};

export type Reminders = {
  enabled: boolean;
  weekday_time: string; // "18:00"
  weekend_time: string;
  timezone: string; // "Europe/Madrid"
  language: string;
  telegram_connected: boolean;
  telegram_available: boolean; // false when the server has no bot
};
