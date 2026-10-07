// These types mirror the JSON that the Django API returns (see src/api/schemas.py).

export type Mood = "tired" | "calm" | "active";

export type Challenge = {
  id: string;
  category: string;
  text: string;
  status: "pending" | "completed";
  accepts_photo: boolean;
  story: string;
};

export type Walk = {
  id: string;
  user_id: string;
  mood: Mood;
  minutes: number;
  weather: string;
  note: string;
  swaps_used: number;
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
