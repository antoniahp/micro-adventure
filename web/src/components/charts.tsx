// Small charts drawn with plain SVG. No library: they are few and simple, and they follow the app's colours.
import type { CSSProperties } from "react";

type BarProps = {
  values: number[];
  labels: string[];
  color: string;
  height?: number;
  highlight?: number; // the bar to draw strong (today, the busiest month); the rest are softer
  ariaLabel: string;
};

// Bars with a label under each one and the value over the strongest.
export function BarChart({ values, labels, color, height = 120, highlight, ariaLabel }: BarProps) {
  const max = Math.max(1, ...values);
  const width = 300;
  const slot = width / values.length;
  const bar = Math.min(26, slot * 0.62);
  const top = 16;
  const base = height - 22;
  return (
    <svg className="chart" viewBox={`0 0 ${width} ${height}`} role="img" aria-label={ariaLabel}>
      <line x1="0" x2={width} y1={base} y2={base} stroke="var(--line)" strokeWidth="1" />
      {values.map((value, i) => {
        const h = value === 0 ? 0 : Math.max(4, ((base - top) * value) / max);
        const x = i * slot + (slot - bar) / 2;
        const strong = highlight === undefined || highlight === i;
        return (
          <g key={i}>
            {value === 0 && <circle cx={x + bar / 2} cy={base - 2} r="2" fill="var(--line)" />}
            {value > 0 && <rect x={x} y={base - h} width={bar} height={h} rx="5" fill={color} opacity={strong ? 1 : 0.45} />}
            {value > 0 && strong && (
              <text x={x + bar / 2} y={base - h - 4} textAnchor="middle" fontSize="10" fontWeight="700" fill="var(--ink)">{value}</text>
            )}
            <text x={x + bar / 2} y={height - 6} textAnchor="middle" fontSize="10" fill="var(--muted)">{labels[i]}</text>
          </g>
        );
      })}
    </svg>
  );
}

type Part = { key: string; value: number; color: string; label: string };

// One bar split in parts (the moods of the week), with its legend.
export function ShareBar({ parts, ariaLabel }: { parts: Part[]; ariaLabel: string }) {
  const total = parts.reduce((sum, p) => sum + p.value, 0);
  if (total === 0) return null;
  return (
    <div>
      <div className="share-bar" role="img" aria-label={ariaLabel}>
        {parts.filter((p) => p.value > 0).map((p) => (
          <span key={p.key} style={{ width: `${(p.value / total) * 100}%`, background: p.color }} />
        ))}
      </div>
      <ul className="share-legend">
        {parts.filter((p) => p.value > 0).map((p) => (
          <li key={p.key}><i style={{ background: p.color }} /> {p.label} <b>{p.value}</b></li>
        ))}
      </ul>
    </div>
  );
}

// Horizontal bars, one per row (the categories).
export function RowBars({ rows }: { rows: { key: string; label: string; value: number; color: string }[] }) {
  const max = Math.max(1, ...rows.map((r) => r.value));
  return (
    <ul className="row-bars">
      {rows.map((r) => (
        <li key={r.key} style={{ "--c": r.color } as CSSProperties}>
          <span>{r.label}</span>
          <span className="row-track"><span style={{ width: `${(r.value / max) * 100}%` }} /></span>
          <b>{r.value}</b>
        </li>
      ))}
    </ul>
  );
}

// A line through the months that have a value (the average feeling, from 1 to 5). Gaps are left empty.
export function FeelingLine({ values, labels, ariaLabel }: { values: (number | null)[]; labels: string[]; ariaLabel: string }) {
  const width = 300, height = 110, left = 14, right = 10, top = 10, base = 86;
  const x = (i: number) => left + ((width - left - right) * i) / (values.length - 1);
  const y = (v: number) => base - ((base - top) * (v - 1)) / 4;
  const points = values.map((v, i) => (v === null ? null : { x: x(i), y: y(v), v }));
  const segments: string[] = [];
  let current: string[] = [];
  points.forEach((p) => {
    if (p) current.push(`${p.x},${p.y}`);
    else if (current.length) { segments.push(current.join(" ")); current = []; }
  });
  if (current.length) segments.push(current.join(" "));
  return (
    <svg className="chart" viewBox={`0 0 ${width} ${height}`} role="img" aria-label={ariaLabel}>
      {[1, 3, 5].map((level) => (
        <g key={level}>
          <line x1={left} x2={width - right} y1={y(level)} y2={y(level)} stroke="var(--line)" strokeDasharray="3 4" />
          <text x="0" y={y(level) + 3} fontSize="9" fill="var(--muted)">{level}</text>
        </g>
      ))}
      {segments.map((pts) => <polyline key={pts} points={pts} fill="none" stroke="var(--violet)" strokeWidth="2.5" strokeLinejoin="round" strokeLinecap="round" />)}
      {points.map((p, i) => p && <circle key={i} cx={p.x} cy={p.y} r="4" fill="var(--paper)" stroke="var(--violet)" strokeWidth="2.5" />)}
      {labels.map((label, i) => <text key={i} x={x(i)} y={height - 6} textAnchor="middle" fontSize="10" fill="var(--muted)">{label}</text>)}
    </svg>
  );
}
