import { useCallback, useEffect, useState, type CSSProperties } from "react";
import { getWeeklySummary, getYearlySummary, saveWeeklyFeeling } from "../api";
import { BarChart, FeelingLine, RowBars, ShareBar, WeekStrip } from "../components/charts";
import Icon, { type IconName } from "../components/Icon";
import { useI18n, type TextKey } from "../i18n";
import { getUserId } from "../storage";
import type { WeeklySummary, YearlySummary } from "../types";
import { CATEGORIES } from "../ui";

const MOOD_COLORS: Record<string, string> = { tired: "#2E8BEA", calm: "#10A878", active: "#FFB300" };

function isoDay(date: Date) {
  const y = date.getFullYear(), m = String(date.getMonth() + 1).padStart(2, "0"), d = String(date.getDate()).padStart(2, "0");
  return `${y}-${m}-${d}`;
}

function atNoon(iso: string) {
  return new Date(`${iso}T12:00:00`); // noon, so no time zone can move it to another day
}

function addDays(iso: string, days: number) {
  const date = atNoon(iso);
  date.setDate(date.getDate() + days);
  return isoDay(date);
}

function formatMinutes(minutes: number) {
  if (minutes < 60) return `${minutes} min`;
  const rest = minutes % 60;
  return rest ? `${Math.floor(minutes / 60)} h ${rest} min` : `${Math.floor(minutes / 60)} h`;
}

function formatKm(km: number) {
  return `${Number.isInteger(km) ? km : km.toFixed(1)} km`;
}

type TileProps = { icon: IconName; color: string; label: string; value: string; note?: string };

// A number with its name, like the cards of a health app.
function Tile({ icon, color, label, value, note }: TileProps) {
  return (
    <div className="tile" style={{ "--c": color } as CSSProperties}>
      <span className="tile-icon"><Icon name={icon} size={20} /></span>
      <span className="tile-label">{label}</span>
      <strong className="tile-value">{value}</strong>
      {note && <small className="tile-note">{note}</small>}
    </div>
  );
}

export default function DashboardScreen() {
  const { t, lang } = useI18n();
  const [mode, setMode] = useState<"week" | "year">("week");
  const [week, setWeek] = useState<string | undefined>(undefined); // a day of the week shown; none is the current one
  const [year, setYear] = useState<number | undefined>(undefined);
  const [weekly, setWeekly] = useState<WeeklySummary | null>(null);
  const [yearly, setYearly] = useState<YearlySummary | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    setError("");
    if (mode === "week") getWeeklySummary(getUserId(), week).then(setWeekly).catch((e: Error) => setError(e.message));
    else getYearlySummary(getUserId(), year).then(setYearly).catch((e: Error) => setError(e.message));
  }, [mode, week, year]);

  return (
    <section className="dashboard">
      <h2>{t("dash.title")}</h2>

      <div className="segmented" role="group" aria-label={t("dash.range")}>
        <button aria-pressed={mode === "week"} onClick={() => setMode("week")}>{t("dash.week")}</button>
        <button aria-pressed={mode === "year"} onClick={() => setMode("year")}>{t("dash.year")}</button>
      </div>

      {error && <p className="error" role="alert">{error}</p>}
      {mode === "week" && !error && (weekly ? <WeekView data={weekly} lang={lang} onMove={setWeek} onSaved={() => setWeek(weekly.week_start)} /> : <p className="hint">{t("dash.loading")}</p>)}
      {mode === "year" && !error && (yearly ? <YearView data={yearly} lang={lang} onMove={setYear} /> : <p className="hint">{t("dash.loading")}</p>)}
    </section>
  );
}

function Stepper({ label, prevLabel, nextLabel, onPrev, onNext, nextDisabled }: { label: string; prevLabel: string; nextLabel: string; onPrev: () => void; onNext: () => void; nextDisabled: boolean }) {
  return (
    <div className="stepper">
      <button onClick={onPrev} aria-label={prevLabel}>‹</button>
      <strong aria-live="polite">{label}</strong>
      <button onClick={onNext} aria-label={nextLabel} disabled={nextDisabled}>›</button>
    </div>
  );
}

function delta(now: number, before: number) {
  return now - before;
}

function WeekView({ data, lang, onMove, onSaved }: { data: WeeklySummary; lang: string; onMove: (week: string) => void; onSaved: () => void }) {
  const { t } = useI18n();
  const today = isoDay(new Date());
  const short = new Intl.DateTimeFormat(lang, { day: "numeric", month: "short" });
  const label = `${short.format(atNoon(data.week_start))} – ${short.format(atNoon(data.week_end))}`;
  const weekday = new Intl.DateTimeFormat(lang, { weekday: "narrow" });
  const walkDelta = delta(data.walks_count, data.previous_walks);
  const note = walkDelta > 0 ? t("dash.deltaUp", { n: walkDelta }) : walkDelta < 0 ? t("dash.deltaDown", { n: -walkDelta }) : t("dash.deltaSame");

  return (
    <>
      <Stepper
        label={label}
        prevLabel={t("dash.prevWeek")}
        nextLabel={t("dash.nextWeek")}
        onPrev={() => onMove(addDays(data.week_start, -7))}
        onNext={() => onMove(addDays(data.week_start, 7))}
        nextDisabled={data.week_end >= today}
      />

      <div className="tiles">
        <Tile icon="pin" color="#F25C54" label={t("dash.walks")} value={String(data.walks_count)} note={note} />
        <Tile icon="check" color="#10A878" label={t("dash.challenges")} value={String(data.challenges_completed)} />
        <Tile icon="clock" color="#2E8BEA" label={t("dash.minutes")} value={formatMinutes(data.minutes)} />
        <Tile icon="route" color="#7357E8" label={t("dash.km")} value={formatKm(data.km)} />
      </div>
      <p className="hint">{t("dash.dataNote")}</p>

      {data.walks_count === 0 ? <p className="hint">{t("dash.empty")}</p> : (
        <>
          <div className="panel">
            <h3>{t("dash.perDay")}</h3>
            <WeekStrip
              days={data.days}
              labels={data.days.map((d) => weekday.format(atNoon(d.day)))}
              today={today}
              ariaLabel={t("dash.perDay")}
            />
            <p className="hint">{t("dash.perDayHint")}</p>
          </div>

          <div className="panel">
            <h3>{t("dash.moods")}</h3>
            <ShareBar
              ariaLabel={t("dash.moods")}
              parts={["tired", "calm", "active"].map((m) => ({ key: m, value: data.moods[m] ?? 0, color: MOOD_COLORS[m], label: t(`energy.${m}` as TextKey) }))}
            />
          </div>

          {Object.keys(data.categories).length > 0 && (
            <div className="panel">
              <h3>{t("dash.categories")}</h3>
              <RowBars
                rows={Object.entries(data.categories).sort((a, b) => b[1] - a[1]).map(([code, value]) => ({
                  key: code, value, color: CATEGORIES[code]?.color ?? "#10A878", label: t(`cat.${code}` as TextKey),
                }))}
              />
            </div>
          )}
        </>
      )}

      <FeelingForm data={data} onSaved={onSaved} />
    </>
  );
}

// "How did you feel this week?": one tap from 1 to 5 and, if they want, a few words.
function FeelingForm({ data, onSaved }: { data: WeeklySummary; onSaved: () => void }) {
  const { t } = useI18n();
  const [feeling, setFeeling] = useState<number | null>(data.feeling);
  const [note, setNote] = useState(data.feeling_note);
  const [state, setState] = useState<"idle" | "saving" | "saved">(data.feeling ? "saved" : "idle");
  const [error, setError] = useState("");

  useEffect(() => {
    setFeeling(data.feeling);
    setNote(data.feeling_note);
    setState(data.feeling ? "saved" : "idle");
    setError("");
  }, [data.week_start, data.feeling, data.feeling_note]);

  const save = useCallback(async () => {
    if (!feeling) return;
    setState("saving");
    try {
      await saveWeeklyFeeling(getUserId(), data.week_start, feeling, note);
      setState("saved");
      onSaved();
    } catch (e) {
      setError((e as Error).message);
      setState("idle");
    }
  }, [feeling, note, data.week_start, onSaved]);

  return (
    <div className="panel feeling">
      <h3><Icon name="bulb" size={20} /> {t("dash.feeling.title")}</h3>
      <div className="scale" role="radiogroup" aria-label={t("dash.feeling.title")}>
        {[1, 2, 3, 4, 5].map((level) => (
          <button key={level} role="radio" aria-checked={feeling === level} className={feeling === level ? "on" : ""} onClick={() => { setFeeling(level); setState("idle"); }}>
            <b>{level}</b>
            <span>{t(`dash.feeling.${level}` as TextKey)}</span>
          </button>
        ))}
      </div>
      <div className="field">
        <label htmlFor="feeling-note">{t("dash.feeling.note")}</label>
        <textarea id="feeling-note" maxLength={500} value={note} onChange={(e) => { setNote(e.target.value); setState("idle"); }} />
      </div>
      {error && <p className="error" role="alert">{error}</p>}
      <div className="story-actions">
        <button className="btn btn-primary" disabled={!feeling || state === "saving"} onClick={save}>
          {state === "saving" ? t("dash.feeling.saving") : t("dash.feeling.save")}
        </button>
        {state === "saved" && <span className="ok-line" role="status"><Icon name="check" size={18} /> {t("dash.feeling.saved")}</span>}
      </div>
    </div>
  );
}

function YearView({ data, lang, onMove }: { data: YearlySummary; lang: string; onMove: (year: number) => void }) {
  const { t } = useI18n();
  const month = new Intl.DateTimeFormat(lang, { month: "narrow" });
  const monthLong = new Intl.DateTimeFormat(lang, { month: "long" });
  const weekday = new Intl.DateTimeFormat(lang, { weekday: "narrow" });
  const monday = new Date(2026, 9, 5, 12); // a Monday: the labels run from Monday to Sunday
  const weekdayLabels = Array.from({ length: 7 }, (_, i) => weekday.format(new Date(monday.getFullYear(), monday.getMonth(), monday.getDate() + i, 12)));
  const oldest = Math.min(...data.years), newest = Math.max(...data.years);
  const busiest = Math.max(...data.weekdays);
  const hasFeelings = data.months.some((m) => m.feeling !== null);

  return (
    <>
      <Stepper
        label={String(data.year)}
        prevLabel={t("dash.prevYear")}
        nextLabel={t("dash.nextYear")}
        onPrev={() => onMove(data.year - 1)}
        onNext={() => onMove(data.year + 1)}
        nextDisabled={data.year >= newest}
      />
      {data.year <= oldest && null}

      <div className="tiles">
        <Tile icon="pin" color="#F25C54" label={t("dash.walks")} value={String(data.walks_count)} note={t("dash.days", { n: data.days_walked })} />
        <Tile icon="check" color="#10A878" label={t("dash.challenges")} value={String(data.challenges_completed)} note={`${data.perfect_walks} ${t("dash.perfect").toLowerCase()}`} />
        <Tile icon="clock" color="#2E8BEA" label={t("dash.minutes")} value={formatMinutes(data.minutes)} />
        <Tile icon="route" color="#7357E8" label={t("dash.km")} value={formatKm(data.km)} />
        <Tile icon="flame" color="#FFB300" label={t("dash.longestStreak")} value={t("dash.days", { n: data.longest_streak })} />
        <Tile icon="chat" color="#F25C54" label={t("dash.stories")} value={String(data.stories)} note={data.best_month ? `${t("dash.bestMonth")}: ${monthLong.format(new Date(data.year, data.best_month - 1, 1, 12))}` : undefined} />
      </div>
      <p className="hint">{t("dash.dataNote")}</p>

      {data.walks_count === 0 ? <p className="hint">{t("dash.empty")}</p> : (
        <>
          <div className="panel">
            <h3>{t("dash.perMonth")}</h3>
            <BarChart
              values={data.months.map((m) => m.walks)}
              labels={data.months.map((m) => month.format(new Date(data.year, m.month - 1, 1, 12)))}
              color="#F25C54"
              highlight={data.best_month ? data.best_month - 1 : undefined}
              ariaLabel={t("dash.perMonth")}
            />
          </div>

          <div className="panel">
            <h3>{t("dash.weekdays")}</h3>
            <BarChart
              values={data.weekdays}
              labels={weekdayLabels}
              color="#2E8BEA"
              highlight={busiest > 0 ? data.weekdays.indexOf(busiest) : undefined}
              ariaLabel={t("dash.weekdays")}
              height={110}
            />
          </div>

          <div className="panel">
            <h3>{t("dash.moods")}</h3>
            <ShareBar
              ariaLabel={t("dash.moods")}
              parts={["tired", "calm", "active"].map((m) => ({ key: m, value: data.moods[m] ?? 0, color: MOOD_COLORS[m], label: t(`energy.${m}` as TextKey) }))}
            />
          </div>

          {Object.keys(data.categories).length > 0 && (
            <div className="panel">
              <h3>{t("dash.categories")}</h3>
              <RowBars
                rows={Object.entries(data.categories).sort((a, b) => b[1] - a[1]).map(([code, value]) => ({
                  key: code, value, color: CATEGORIES[code]?.color ?? "#10A878", label: t(`cat.${code}` as TextKey),
                }))}
              />
            </div>
          )}
        </>
      )}

      {hasFeelings && (
        <div className="panel">
          <h3>{t("dash.feelingByMonth")}</h3>
          <FeelingLine
            values={data.months.map((m) => m.feeling)}
            labels={data.months.map((m) => month.format(new Date(data.year, m.month - 1, 1, 12)))}
            ariaLabel={t("dash.feelingByMonth")}
          />
        </div>
      )}
    </>
  );
}
