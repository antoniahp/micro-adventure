// Simple line icons (24x24). Each name maps to one or more SVG paths.
const PATHS = {
  hand: ["M8 13V6.5a1.5 1.5 0 0 1 3 0V11", "M11 11V4.5a1.5 1.5 0 0 1 3 0V11", "M14 11V6.5a1.5 1.5 0 0 1 3 0V14a6 6 0 0 1-6 6h-.5A6 6 0 0 1 6 17l-2-3.5a1.5 1.5 0 0 1 2.4-1.7L8 13.5"],
  sound: ["M4 9.5v5h3.5L13 19V5L7.5 9.5H4z", "M16 9a4 4 0 0 1 0 6", "M18.5 6.5a8 8 0 0 1 0 11"],
  landmark: ["M3 10l9-6 9 6", "M5.5 10v8", "M10 10v8", "M14 10v8", "M18.5 10v8", "M3 20.5h18"],
  leaf: ["M5 19C5 10 10.5 5 19.5 4.5 19 13.5 14 19 6 19", "M5 19l8-8"],
  eye: ["M2 12s3.6-6.5 10-6.5S22 12 22 12s-3.6 6.5-10 6.5S2 12 2 12z", "M12 14.8a2.8 2.8 0 1 0 0-5.6 2.8 2.8 0 0 0 0 5.6z"],
  sun: ["M12 16.5a4.5 4.5 0 1 0 0-9 4.5 4.5 0 0 0 0 9z", "M12 2.5v2", "M12 19.5v2", "M2.5 12h2", "M19.5 12h2", "M5.3 5.3l1.4 1.4", "M17.3 17.3l1.4 1.4", "M18.7 5.3l-1.4 1.4", "M6.7 17.3l-1.4 1.4"],
  cloud: ["M7 18.5a4 4 0 0 1-.6-7.95A5.5 5.5 0 0 1 17 9.5a4.5 4.5 0 0 1 .5 9H7z"],
  rain: ["M7 15a4 4 0 0 1-.6-7.95A5.5 5.5 0 0 1 17 6a4.5 4.5 0 0 1 .5 9H7z", "M8.5 18.5l-1 2", "M12.5 18.5l-1 2", "M16.5 18.5l-1 2"],
  check: ["M5 12.5l4.5 4.5L19 7.5"],
  compass: ["M12 21a9 9 0 1 0 0-18 9 9 0 0 0 0 18z", "M15.5 8.5l-2 5-5 2 2-5 5-2z"],
  book: ["M5 4.5h11a3 3 0 0 1 3 3v12H8a3 3 0 0 1-3-3v-12z", "M5 16.5a3 3 0 0 1 3-3h11"],
  lock: ["M6 11h12v9H6z", "M8.5 11V8a3.5 3.5 0 0 1 7 0v3"],
  star: ["M12 3.5l2.6 5.4 5.9.8-4.3 4.1 1 5.9L12 16.9 6.8 19.7l1-5.9L3.5 9.7l5.9-.8L12 3.5z"],
  mic: ["M12 15a3 3 0 0 0 3-3V6a3 3 0 0 0-6 0v6a3 3 0 0 0 3 3z", "M6 11.5a6 6 0 0 0 12 0", "M12 17.5V21"],
  pen: ["M4 20l1-4L16.5 4.5a2 2 0 0 1 3 3L8 19l-4 1z", "M14.5 6.5l3 3"],
  stop: ["M7 7h10v10H7z"],
  camera: ["M4 8h3l1.5-2h7L17 8h3v11H4z", "M12 16.5a3.5 3.5 0 1 0 0-7 3.5 3.5 0 0 0 0 7z"],
  pin: ["M12 21s-6.5-5.5-6.5-10.5a6.5 6.5 0 0 1 13 0C18.5 15.5 12 21 12 21z", "M12 12.7a2.2 2.2 0 1 0 0-4.4 2.2 2.2 0 0 0 0 4.4z"],
} as const;

export type IconName = keyof typeof PATHS;

export default function Icon({ name, size = 24 }: { name: IconName; size?: number }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
      {PATHS[name].map((d) => (
        <path key={d} d={d} />
      ))}
    </svg>
  );
}
