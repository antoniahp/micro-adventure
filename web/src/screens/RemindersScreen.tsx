import { useEffect, useRef, useState } from "react";
import { getReminders, linkTelegram, saveReminders, unlinkTelegram } from "../api";
import { getPlace } from "../location";
import Icon from "../components/Icon";
import { useI18n } from "../i18n";
import { useInstall } from "../pwa";
import { getUserId } from "../storage";
import type { Place, Reminders } from "../types";

const POLL_EVERY_MS = 3000;
const POLL_FOR_MS = 3 * 60 * 1000; // the person has three minutes to press Start in Telegram

export default function RemindersScreen() {
  const { t } = useI18n();
  const install = useInstall();
  const userId = getUserId();
  const [settings, setSettings] = useState<Reminders | null>(null);
  const [enabled, setEnabled] = useState(false);
  const [weekday, setWeekday] = useState("18:00");
  const [weekend, setWeekend] = useState("11:00");
  const [shareWeather, setShareWeather] = useState(false);
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);
  const [error, setError] = useState("");
  const [telegramUrl, setTelegramUrl] = useState(""); // set while we wait for the person to press Start
  const poll = useRef<ReturnType<typeof setInterval> | null>(null);

  function show(loaded: Reminders) {
    setSettings(loaded);
    setEnabled(loaded.enabled);
    setWeekday(loaded.weekday_time);
    setWeekend(loaded.weekend_time);
    setShareWeather(loaded.has_place);
  }

  useEffect(() => {
    getReminders(userId).then(show).catch((e: Error) => setError(e.message));
    return stopWaiting;
  }, [userId]);

  function stopWaiting() {
    if (poll.current) clearInterval(poll.current);
    poll.current = null;
    setTelegramUrl("");
  }

  // Opens the bot in Telegram and checks every few seconds whether the person has pressed Start.
  async function connect() {
    setError("");
    try {
      const url = await linkTelegram(userId);
      setTelegramUrl(url);
      window.open(url, "_blank", "noopener");
      const startedAt = Date.now();
      poll.current = setInterval(async () => {
        try {
          const latest = await getReminders(userId);
          if (latest.telegram_connected) {
            stopWaiting();
            show(latest);
          } else if (Date.now() - startedAt > POLL_FOR_MS) {
            stopWaiting();
          }
        } catch {
          /* it tries again on the next turn */
        }
      }, POLL_EVERY_MS);
    } catch (e) {
      setError((e as Error).message);
    }
  }

  async function disconnect() {
    setError("");
    try {
      await unlinkTelegram(userId);
      show(await getReminders(userId));
    } catch (e) {
      setError((e as Error).message);
    }
  }

  async function save() {
    setSaving(true);
    setSaved(false);
    setError("");
    try {
      // The place is only asked for when the person wants the weather in the reminder, and it is taken away when they do not.
      let place: Place | null | undefined = undefined;
      if (shareWeather) {
        try {
          place = await getPlace();
        } catch {
          setShareWeather(false);
          setError(t("error.noPlace"));
          place = settings?.has_place ? null : undefined;
        }
      } else if (settings?.has_place) {
        place = null;
      }
      show(await saveReminders(userId, { enabled, weekdayTime: weekday, weekendTime: weekend, place }));
      setSaved(true);
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setSaving(false);
    }
  }

  const locked = !settings?.telegram_connected;

  if (!settings) return error ? <p className="error" role="alert">{error}</p> : <p className="hint">…</p>;

  return (
    <section className="reminders">
      <h2>{t("reminders.title")}</h2>
      <p className="hint">{t("reminders.intro")}</p>

      <div className="panel">
        <h3><Icon name="send" size={20} /> {t("reminders.telegram")}</h3>
        {!settings.telegram_available ? (
          <p className="hint">{t("reminders.unavailable")}</p>
        ) : settings.telegram_connected ? (
          <>
            <p className="ok-line"><Icon name="check" size={18} /> {t("reminders.connected")}</p>
            <button className="btn btn-link left" onClick={disconnect}>{t("reminders.disconnect")}</button>
          </>
        ) : telegramUrl ? (
          <>
            <p className="hint" role="status">{t("reminders.waiting")}</p>
            <a className="btn btn-secondary" href={telegramUrl} target="_blank" rel="noopener noreferrer">{t("reminders.reopen")}</a>
          </>
        ) : (
          <>
            <p className="hint">{t("reminders.notConnected")}</p>
            <button className="btn btn-primary" onClick={connect}><Icon name="send" size={18} /> {t("reminders.connect")}</button>
          </>
        )}
      </div>

      {(
        <div className={locked ? "panel dimmed" : "panel"}>
          <h3><Icon name="bell" size={20} /> {t("reminders.when")}</h3>
          {locked && <p className="hint">{t("reminders.needTelegram")}</p>}
          <label className="switch">
            <span>{t("reminders.on")}</span>
            <input type="checkbox" role="switch" disabled={locked} checked={enabled} onChange={(e) => { setEnabled(e.target.checked); setSaved(false); }} />
            <span className="track" aria-hidden="true" />
          </label>
          <div className="time-row">
            <div className="field">
              <label htmlFor="weekday-time">{t("reminders.weekday")}</label>
              <input id="weekday-time" type="time" disabled={locked} value={weekday} onChange={(e) => { setWeekday(e.target.value); setSaved(false); }} />
            </div>
            <div className="field">
              <label htmlFor="weekend-time">{t("reminders.weekend")}</label>
              <input id="weekend-time" type="time" disabled={locked} value={weekend} onChange={(e) => { setWeekend(e.target.value); setSaved(false); }} />
            </div>
          </div>
          <p className="hint">{t("reminders.hint")}</p>
          <label className="switch">
            <span>{t("reminders.weather")}</span>
            <input type="checkbox" role="switch" disabled={locked} checked={shareWeather} onChange={(e) => { setShareWeather(e.target.checked); setSaved(false); }} />
            <span className="track" aria-hidden="true" />
          </label>
          <p className="hint">{t("reminders.weatherHint")}</p>
          <div className="story-actions">
            <button className="btn btn-primary" disabled={locked || saving || !weekday || !weekend} onClick={save}>
              {saving ? t("reminders.saving") : t("reminders.save")}
            </button>
            {saved && <span className="ok-line" role="status"><Icon name="check" size={18} /> {t("reminders.saved")}</span>}
          </div>
        </div>
      )}

      {error && <p className="error" role="alert">{error}</p>}

      {!install.installed && (
      <div className="panel">
        <h3><Icon name="download" size={20} /> {t("reminders.install")}</h3>
        <p className="hint">{t("reminders.installWhy")}</p>
        {install.canInstall ? (
          <button className="btn btn-primary" onClick={install.install}><Icon name="download" size={18} /> {t("reminders.installButton")}</button>
        ) : (
          <p className="hint">{install.ios ? t("reminders.installIos") : t("reminders.installOther")}</p>
        )}
      </div>
      )}
    </section>
  );
}
