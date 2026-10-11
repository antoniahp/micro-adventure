import { useCallback, useEffect, useLayoutEffect, useRef, useState } from "react";
import { useI18n } from "../i18n";

export type TourStep = { target: string; title: string; text: string };

type Box = { top: number; left: number; width: number; height: number };

const GAP = 12; // between the highlighted element and the bubble
const MARGIN = 16; // the bubble never touches the screen edge
const PAD = 6; // the highlight is a little larger than the element

const EDGE = 3; // the highlight's outline stays inside the screen, even for the first and last tab

function boxOf(element: Element): Box {
  const r = element.getBoundingClientRect();
  const left = Math.max(EDGE, r.left - PAD);
  const top = Math.max(EDGE, r.top - PAD);
  const right = Math.min(window.innerWidth - EDGE, r.right + PAD);
  const bottom = Math.min(window.innerHeight - EDGE, r.bottom + PAD);
  return { top, left, width: right - left, height: bottom - top };
}

// A few bubbles, one at a time, each pointing at a real element on screen (found by its data-tour name).
// Steps whose element isn't on screen are skipped, so the same guide works with or without, say, a photo button.
export default function Tour({ steps, onDone }: { steps: TourStep[]; onDone: () => void }) {
  const { t } = useI18n();
  const available = steps.filter((step) => document.querySelector(`[data-tour="${step.target}"]`));
  const [index, setIndex] = useState(0);
  const [box, setBox] = useState<Box | null>(null);
  const [bubbleHeight, setBubbleHeight] = useState(0);
  const bubble = useRef<HTMLDivElement | null>(null);
  const next = useRef<HTMLButtonElement | null>(null);
  const step = available[index];

  const measure = useCallback(() => {
    const element = step && document.querySelector(`[data-tour="${step.target}"]`);
    setBox(element ? boxOf(element) : null);
  }, [step]);

  // Bring the element into view first, then measure it where it ended up.
  useEffect(() => {
    if (!step) return;
    const element = document.querySelector(`[data-tour="${step.target}"]`);
    element?.scrollIntoView({ block: "center", behavior: "auto" });
    measure();
    next.current?.focus();
  }, [step, measure]);

  useEffect(() => {
    window.addEventListener("resize", measure);
    window.addEventListener("scroll", measure, true);
    return () => {
      window.removeEventListener("resize", measure);
      window.removeEventListener("scroll", measure, true);
    };
  }, [measure]);

  useLayoutEffect(() => {
    if (bubble.current) setBubbleHeight(bubble.current.offsetHeight);
  }, [index, box]);

  useEffect(() => {
    if (!step) onDone(); // nothing on screen to point at
  }, [step, onDone]);

  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") onDone();
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [onDone]);

  if (!step || !box) return null;

  const last = index === available.length - 1;
  const width = Math.min(320, window.innerWidth - MARGIN * 2);
  const left = Math.min(Math.max(box.left + box.width / 2 - width / 2, MARGIN), window.innerWidth - width - MARGIN);
  const below = box.top + box.height + GAP;
  const fitsBelow = below + bubbleHeight + MARGIN <= window.innerHeight;
  const top = fitsBelow ? below : Math.max(MARGIN, box.top - GAP - bubbleHeight);

  return (
    <div className="tour" role="dialog" aria-modal="true" aria-labelledby="tour-title" aria-describedby="tour-text">
      <div className="tour-spot" style={{ top: box.top, left: box.left, width: box.width, height: box.height }} aria-hidden="true" />
      <div className="tour-bubble" ref={bubble} style={{ top, left, width }}>
        <p className="tour-count">{t("tour.count", { n: index + 1, total: available.length })}</p>
        <h3 id="tour-title">{step.title}</h3>
        <p id="tour-text">{step.text}</p>
        <div className="tour-actions">
          {!last && <button className="btn btn-link" onClick={onDone}>{t("tour.skip")}</button>}
          <button ref={next} className="btn btn-primary" onClick={() => (last ? onDone() : setIndex(index + 1))}>
            {last ? t("tour.done") : t("tour.next")}
          </button>
        </div>
      </div>
    </div>
  );
}
