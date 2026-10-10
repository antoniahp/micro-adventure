// The anonymous session. The browser has an id and, once the server has accepted it, a pair of tokens:
// a short one that goes in every request and a long one that gets a new pair. Nobody can use an id without them.
import { getUserId, resetUserId, setUserId } from "./storage";

type Tokens = { access: string; refresh: string };
const KEY = "session";

function read(): Tokens | null {
  try {
    const tokens = JSON.parse(localStorage.getItem(KEY) ?? "null");
    return tokens?.access && tokens?.refresh ? tokens : null;
  } catch {
    return null;
  }
}

function save(session: Tokens & { user_id: string }) {
  localStorage.setItem(KEY, JSON.stringify({ access: session.access, refresh: session.refresh }));
  setUserId(session.user_id);
}

function post(path: string, body: object) {
  return fetch(`/api/auth${path}`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) });
}

export function accessToken(): string | null {
  return read()?.access ?? null;
}

// Two screens asking at once must share one request, or the second would find the id already taken.
let pending: Promise<boolean> | null = null;
function once(work: () => Promise<boolean>): Promise<boolean> {
  pending ??= work().finally(() => (pending = null));
  return pending;
}

async function start(): Promise<boolean> {
  for (let attempt = 0; attempt < 2; attempt++) {
    const response = await post("/start", { user_id: getUserId() });
    if (response.ok) {
      save(await response.json());
      return true;
    }
    // The id already has a session somewhere and this browser lost its tokens: begin again with a new one.
    if (response.status === 409 && attempt === 0) resetUserId();
    else return false;
  }
  return false;
}

export const ensureSession = () => (read() ? Promise.resolve(true) : once(start));

// Called when the server says 401: the short token ran out. Without a valid long one, the session starts again.
export function renewSession(): Promise<boolean> {
  return once(async () => {
    const tokens = read();
    if (tokens) {
      const response = await post("/refresh", { refresh: tokens.refresh });
      if (response.ok) {
        save(await response.json());
        return true;
      }
      localStorage.removeItem(KEY);
    }
    return start();
  });
}
