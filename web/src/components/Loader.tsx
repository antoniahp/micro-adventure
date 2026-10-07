import { useEffect, useState } from "react";

// Shown while the model writes the challenges, which can take a few seconds.
// The messages rotate so the wait feels like part of the walk.
const MESSAGES = [
  "Buscando algo que tocar…",
  "Afinando el oído…",
  "Eligiendo un rincón con historia…",
  "Preparando tu cuaderno…",
];

export default function Loader({ title }: { title: string }) {
  const [index, setIndex] = useState(0);

  useEffect(() => {
    const timer = setInterval(() => setIndex((i) => (i + 1) % MESSAGES.length), 2200);
    return () => clearInterval(timer);
  }, []);

  return (
    <div className="loader" role="status">
      <div className="steps" aria-hidden="true"><span /><span /><span /><span /></div>
      <h2>{title}</h2>
      <p>{MESSAGES[index]}</p>
    </div>
  );
}
