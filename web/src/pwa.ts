// Installing the web as an app (PWA): the service worker, and the "install" button of the browser.
import { useEffect, useState } from "react";

// The browser fires this event once, early, when the app can be installed. We keep it to use it from a button.
type InstallPromptEvent = Event & { prompt: () => Promise<void>; userChoice: Promise<{ outcome: "accepted" | "dismissed" }> };
let savedPrompt: InstallPromptEvent | null = null;
const listeners = new Set<() => void>();

if (typeof window !== "undefined") {
  window.addEventListener("beforeinstallprompt", (event) => {
    event.preventDefault();
    savedPrompt = event as InstallPromptEvent;
    listeners.forEach((listener) => listener());
  });
  window.addEventListener("appinstalled", () => {
    savedPrompt = null;
    listeners.forEach((listener) => listener());
  });
}

// Only in production: in development a service worker would keep serving old files.
export function registerServiceWorker() {
  if (!import.meta.env.PROD || !("serviceWorker" in navigator)) return;
  window.addEventListener("load", () => {
    navigator.serviceWorker.register("/sw.js").catch(() => {}); // not essential: the web works without it
  });
}

export function isInstalled(): boolean {
  return window.matchMedia("(display-mode: standalone)").matches || (navigator as Navigator & { standalone?: boolean }).standalone === true;
}

// iPhones and iPads have no install button: the person adds the app from the Share menu.
export function isIos(): boolean {
  return /iphone|ipad|ipod/i.test(navigator.userAgent) || (navigator.platform === "MacIntel" && navigator.maxTouchPoints > 1);
}

export function useInstall() {
  const [, refresh] = useState(0);
  useEffect(() => {
    const listener = () => refresh((n) => n + 1);
    listeners.add(listener);
    return () => {
      listeners.delete(listener);
    };
  }, []);

  async function install() {
    if (!savedPrompt) return;
    await savedPrompt.prompt();
    await savedPrompt.userChoice;
    savedPrompt = null;
    refresh((n) => n + 1);
  }

  return { installed: isInstalled(), canInstall: savedPrompt !== null, ios: isIos(), install };
}
