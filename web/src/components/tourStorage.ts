// Which short guides this person has already seen. Kept on the phone only: a guide is a convenience, so if the
// browser forgets (private window, cleared data) the worst case is seeing it once more.
export type TourName = "app" | "walk";

const KEY = (name: TourName) => `tour.${name}.done`;
const RESTART = "tour:restart";

export function tourSeen(name: TourName): boolean {
  try {
    return localStorage.getItem(KEY(name)) === "1";
  } catch {
    return true; // no storage: better never to show it than to show it on every visit
  }
}

export function markTourSeen(name: TourName) {
  try {
    localStorage.setItem(KEY(name), "1");
  } catch {
    /* nothing to keep */
  }
}

// "See the guide again" in Settings: both guides become new again, and the app guide starts right away.
export function restartTours() {
  try {
    localStorage.removeItem(KEY("app"));
    localStorage.removeItem(KEY("walk"));
  } catch {
    /* the event below still shows the app guide once */
  }
  window.dispatchEvent(new Event(RESTART));
}

export function onToursRestarted(listener: () => void): () => void {
  window.addEventListener(RESTART, listener);
  return () => window.removeEventListener(RESTART, listener);
}
