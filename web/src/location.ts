import type { Place } from "./types";

const KEY = "sharesPlace"; // set once the person has allowed it, so the next visit does not ask again

export function rememberedPlaceAllowed(): boolean {
  try {
    return localStorage.getItem(KEY) === "1";
  } catch {
    return false;
  }
}

// Asks the browser where the person is. The answer is rounded to about a kilometre: the weather needs no more.
export function getPlace(): Promise<Place> {
  return new Promise((resolve, reject) => {
    if (!("geolocation" in navigator)) return reject(new Error("unsupported"));
    navigator.geolocation.getCurrentPosition(
      (position) => {
        try {
          localStorage.setItem(KEY, "1");
        } catch {
          /* private mode: it just asks again next time */
        }
        resolve({ latitude: Math.round(position.coords.latitude * 100) / 100, longitude: Math.round(position.coords.longitude * 100) / 100 });
      },
      (error) => reject(new Error(error.code === error.PERMISSION_DENIED ? "denied" : "unavailable")),
      { enableHighAccuracy: false, timeout: 8000, maximumAge: 10 * 60 * 1000 },
    );
  });
}
