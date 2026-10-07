// All the calls to the backend live in this file. Screens never use fetch directly.
import type { Mood, Progress, Walk } from "./types";

const MAX_SWAPS_PER_WALK = 2; // same rule as the backend (Walk.MAX_SWAPS_PER_WALK)
export { MAX_SWAPS_PER_WALK };

class ApiError extends Error {
  constructor(message: string, public status: number) {
    super(message);
  }
}

async function request<T>(path: string, init?: RequestInit): Promise<T | undefined> {
  const response = await fetch(`/api${path}`, init);
  if (!response.ok) {
    // Domain errors come as {"detail": "..."}; anything else gets a generic message.
    const body = await response.json().catch(() => null);
    throw new ApiError(body?.detail ?? "Algo ha fallado. Inténtalo de nuevo.", response.status);
  }
  return response.status === 204 ? undefined : response.json();
}

// Asks the backend to load the model. Called when the form opens, so it is ready when the person submits.
export async function warmUp() {
  await request("/warmup", { method: "POST" });
}

export async function startWalk(userId: string, mood: Mood, minutes: number, weather: string, note: string) {
  const created = await request<{ id: string }>("/walks", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ user_id: userId, mood, minutes, weather, note }),
  });
  return created!.id;
}

export async function getWalk(walkId: string) {
  return (await request<Walk>(`/walks/${walkId}`))!;
}

// A challenge is completed with a story (written or from a voice note), a photo, or both.
export async function completeChallenge(walkId: string, challengeId: string, answer: { photo?: File; story?: string }) {
  const form = new FormData();
  if (answer.photo) form.append("photo", answer.photo);
  if (answer.story) form.append("story", answer.story);
  await request(`/walks/${walkId}/challenges/${challengeId}/complete`, { method: "POST", body: form });
}

export async function swapChallenge(walkId: string, challengeId: string) {
  await request(`/walks/${walkId}/challenges/${challengeId}/swap`, { method: "POST" });
}

export async function getProgress(userId: string) {
  return (await request<Progress>(`/users/${userId}/progress`))!;
}

// Turns a voice note into text. The person reads and fixes the text before sending it.
export async function transcribe(audio: Blob) {
  const form = new FormData();
  form.append("audio", audio, "voice-note");
  try {
    const result = await request<{ text: string }>("/transcribe", { method: "POST", body: form });
    return result!.text;
  } catch (e) {
    if (e instanceof ApiError && e.status === 503) throw new Error("La voz no está activada todavía. Escríbelo, por favor.");
    if (e instanceof ApiError && e.status === 502) throw new Error("No he podido entender el audio. Prueba otra vez o escríbelo.");
    throw e;
  }
}
