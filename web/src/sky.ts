// The sky on the start screen follows the hour on the person's own device, so it follows
// their time zone with no extra code. Open the app with ?hour=21 to preview any hour.
import { useEffect, useState } from "react";

// Colours of the sky at some hours. Between two of them the colour is blended.
const STOPS: { hour: number; top: string; bottom: string }[] = [
  { hour: 0, top: "#0B1030", bottom: "#1E2160" },
  { hour: 5, top: "#161A52", bottom: "#3A3589" },
  { hour: 6.5, top: "#5457C2", bottom: "#FF9A8B" }, // dawn
  { hour: 8.5, top: "#3F86DB", bottom: "#A9D6FF" },
  { hour: 12, top: "#2A78D0", bottom: "#8EC9FF" },
  { hour: 16.5, top: "#2F7FD6", bottom: "#A5CBF5" },
  { hour: 18.5, top: "#3B3A99", bottom: "#FF8A5B" }, // sunset
  { hour: 20, top: "#25235F", bottom: "#6A4BB0" }, // dusk
  { hour: 22, top: "#11143F", bottom: "#232770" },
  { hour: 24, top: "#0B1030", bottom: "#1E2160" },
];

export type Sky = {
  top: string;
  bottom: string;
  sun: { x: number; y: number; color: string } | null;
  moon: { x: number; y: number } | null;
  night: number; // 0 = full day, 1 = full night (stars, fireflies, dark tint)
  lamp: number; // how bright the street lamp is
};

function hexToRgb(hex: string): [number, number, number] {
  return [1, 3, 5].map((i) => parseInt(hex.slice(i, i + 2), 16)) as [number, number, number];
}

function mix(a: string, b: string, amount: number): string {
  const [from, to] = [hexToRgb(a), hexToRgb(b)];
  const channel = (i: number) => Math.round(from[i] + (to[i] - from[i]) * amount);
  return `rgb(${channel(0)} ${channel(1)} ${channel(2)})`;
}

const clamp = (value: number) => Math.min(1, Math.max(0, value));
const ramp = (value: number, from: number, to: number) => clamp((value - from) / (to - from));

export function skyAt(hour: number): Sky {
  const h = ((hour % 24) + 24) % 24;
  const index = STOPS.findIndex((stop, i) => h >= stop.hour && h <= STOPS[i + 1].hour);
  const [a, b] = [STOPS[index], STOPS[index + 1]];
  const amount = (h - a.hour) / (b.hour - a.hour);

  // The sun crosses the sky from 6:00 to 19:30, the moon from 19:30 to 6:00.
  const sunProgress = (h - 6) / 13.5;
  const moonProgress = ((h < 12 ? h + 24 : h) - 19.5) / 10.5;
  const nearHorizon = 1 - clamp(Math.min(sunProgress, 1 - sunProgress) / 0.2);
  const arc = (progress: number, peak: number) => ({ x: 140 + progress * 230, y: 138 - Math.sin(Math.PI * progress) * (138 - peak) });

  return {
    top: mix(a.top, b.top, amount),
    bottom: mix(a.bottom, b.bottom, amount),
    sun: sunProgress >= 0 && sunProgress <= 1 ? { ...arc(sunProgress, 64), color: mix("#FFB300", "#FF6F3C", nearHorizon) } : null,
    moon: moonProgress >= 0 && moonProgress <= 1 ? arc(moonProgress, 58) : null,
    night: h >= 12 ? ramp(h, 20, 21.5) : 1 - ramp(h, 5, 6.5),
    lamp: h >= 12 ? ramp(h, 17.5, 19) : 1 - ramp(h, 6.5, 8),
  };
}

function deviceHour(): number {
  const forced = new URLSearchParams(window.location.search).get("hour");
  if (forced !== null && !Number.isNaN(Number(forced))) return Number(forced);
  const now = new Date();
  return now.getHours() + now.getMinutes() / 60;
}

// The sky for right now, refreshed every minute while the screen is open.
export function useSky(): Sky {
  const [sky, setSky] = useState(() => skyAt(deviceHour()));
  useEffect(() => {
    const timer = setInterval(() => setSky(skyAt(deviceHour())), 60_000);
    return () => clearInterval(timer);
  }, []);
  return sky;
}
