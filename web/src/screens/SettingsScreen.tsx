import { useEffect, useRef, useState } from "react";
import { getAccount, linkGoogleAccount, setNickname, unlinkGoogleAccount } from "../api";
import { googleSignInAvailable, renderGoogleSignIn } from "../google";
import Icon from "../components/Icon";
import { useI18n } from "../i18n";
import { adoptSession } from "../session";
import { getUserId } from "../storage";
import type { Account } from "../types";

// Both optional: nothing here is needed to use the app, and leaving it untouched leaves the app
// exactly as it was.
export default function SettingsScreen() {
  const { t, lang } = useI18n();
  const userId = getUserId();
  const [account, setAccount] = useState<Account | null>(null);
  const [nickname, setNicknameField] = useState("");
  const [nicknameSaved, setNicknameSaved] = useState(false);
  const [error, setError] = useState("");
  const [googleError, setGoogleError] = useState("");
  const googleButton = useRef<HTMLDivElement | null>(null);

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

  return (
    <section className="reminders">
      <h2>{t("settings.title")}</h2>
      <p className="hint">{t("settings.intro")}</p>

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

      {error && <p className="error" role="alert">{error}</p>}
    </section>
  );
}
