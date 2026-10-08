import { useEffect, useState } from "react";

import { useI18n } from "../i18n";

// Shown while the model writes the challenges, which can take a few seconds.
// The messages rotate so the wait feels like part of the walk.
const MESSAGES = ["loader.1", "loader.2", "loader.3", "loader.4"] as const;

export default function Loader({ title }: { title: string }) {
  const { t } = useI18n();
  const [index, setIndex] = useState(0);

  useEffect(() => {
    const timer = setInterval(() => setIndex((i) => (i + 1) % MESSAGES.length), 2200);
    return () => clearInterval(timer);
  }, []);

  return (
    <div className="loader" role="status">
      <div className="steps" aria-hidden="true"><span /><span /><span /><span /></div>
      <h2>{title}</h2>
      <p>{t(MESSAGES[index])}</p>
    </div>
  );
}
