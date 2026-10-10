import { useEffect, useRef, useState } from "react";
import { getAccount, getReminders, linkGoogleAccount, linkTelegram, saveReminders, setNickname, unlinkGoogleAccount, unlinkTelegram } from "../api";
import { googleSignInAvailable, renderGoogleSignIn } from "../google";
import { getPlace } from "../location";
import Icon from "../components/Icon";
import { useI18n } from "../i18n";
import { useInstall } from "../pwa";
import { adoptSession } from "../session";
import { getUserId } from "../storage";
import type { Account, Place, Reminders } from "../types";

const POLL_EVERY_MS = 3000;
const POLL_FOR_MS = 3 * 60 * 1000; // the person has three minutes to press Start in Telegram

export default function RemindersScreen() {
  const { t, lang } = useI18n();
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

  // The nickname and the optional Google backup. Both are fully optional: nothing here blocks the
  // reminders above, and leaving them untouched leaves the app exactly as it was.
  const [account, setAccount] = useState<Account | null>(null);
  const [nickname, setNicknameField] = useState("");
  const [nicknameSaved, setNicknameSaved] = useState(false);
  const [googleError, setGoogleError] = useState("");
  const googleButton = useRef<HTMLDivElement | null>(null);

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

  useEffect(() => {
    getAccount(userId).then((loaded) => {
      setAccount(loaded);
      setNicknameField(loaded.nickname ?? "");
    }).catch(() => {
      /* the panels below just stay at their empty defaults */
    });
  }, [userId]);

  useEffect(() => {
    if (!googleSignInAvailable || !googleButton.current || account?.google_linked) return;
    renderGoogleSignIn(googleButton.current, lang)
      .then(async (idToken) => {
        setGoogleError("");
        const result = await linkGoogleAccount(userId, idToken);
        if (result.switched && result.access && result.refresh) {
          adoptSession({ access: result.access, refresh: result.refresh, user_id: result.user_id });
          window.alert(t("account.google.switched"));
          window.location.reload(); // every screen re-reads the restored account from scratch
          return;
        }
        setAccount({ nickname: result.nickname, google_linked: result.google_linked });
      })
      .catch((e: Error) => setGoogleError(e.message || t("error.google")));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [account?.google_linked, userId, lang]);

  async function saveNickname(value: string) {
    const current = account?.nickname ?? "";
    if (value === current) return;
    try {
      const updated = await setNickname(userId, value || null);
      setAccount(updated);
      setNicknameField(updated.nickname ?? "");
      setNicknameSaved(true);
      setTimeout(() => setNicknameSaved(false), 2000);
    } catch (e) {
      setError((e as Error).message);
    }
  }

  async function disconnectGoogle() {
    setGoogleError("");
    try {
      setAccount(await unlinkGoogleAccount(userId));
    } catch (e) {
      setGoogleError((e as Error).message);
    }
  }

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

      <div className="panel">
        <h3><Icon name="user" size={20} /> {t("account.nickname.title")}</h3>
        <input
          type="text"
          value={nickname}
          placeholder={t("account.nickname.placeholder")}
          onChange={(e) => setNicknameField(e.target.value)}
          onBlur={(e) => saveNickname(e.target.value.trim())}
        />
        <p className="hint">{t("account.nickname.hint")}</p>
        {nicknameSaved && <span className="ok-line" role="status"><Icon name="check" size={18} /> {t("account.nickname.saved")}</span>}
        {account?.nickname && (
          <button className="btn btn-link left" onClick={() => saveNickname("")}>{t("account.nickname.remove")}</button>
        )}
      </div>

      <div className="panel">
        <h3><Icon name="lock" size={20} /> {t("account.google.title")}</h3>
        {account?.google_linked ? (
          <>
            <p className="ok-line"><Icon name="check" size={18} /> {t("account.google.connected")}</p>
            <button className="btn btn-link left" onClick={disconnectGoogle}>{t("account.google.disconnect")}</button>
          </>
        ) : (
          <>
            <p className="hint">{t("account.google.why")}</p>
            {googleSignInAvailable ? <div ref={googleButton} /> : <p className="hint">{t("account.google.unavailable")}</p>}
            <p className="hint">{t("account.google.optional")}</p>
          </>
        )}
        {googleError && <p className="error" role="alert">{googleError}</p>}
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
