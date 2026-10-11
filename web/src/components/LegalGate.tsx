import { useState } from "react";
import { acceptLegal } from "../api";
import { useI18n } from "../i18n";
import { getUserId } from "../storage";
import Icon from "./Icon";
import LegalLinks from "./LegalLinks";

// Shown once, before anything else (and again if the policy or terms change): the person reads what the app
// keeps and taps to accept. The server records which version and when, as proof (GDPR art. 5.2).
// Nothing is pre-ticked and nothing is accepted by scrolling: only the button counts.
export default function LegalGate({ onAccepted }: { onAccepted: () => void }) {
  const { t } = useI18n();
  const [sending, setSending] = useState(false);
  const [error, setError] = useState("");

  async function accept() {
    setError("");
    setSending(true);
    try {
      await acceptLegal(getUserId());
      onAccepted();
    } catch (e) {
      setError((e as Error).message);
      setSending(false);
    }
  }

  return (
    <section className="legal-gate" aria-labelledby="legal-gate-title">
      <h2 id="legal-gate-title">{t("legal.gate.title")}</h2>
      <div className="panel">
        <p>{t("legal.gate.text")}</p>
        <ul className="legal-gate-points">
          <li><Icon name="lock" size={18} /> {t("legal.gate.point.anonymous")}</li>
          <li><Icon name="check" size={18} /> {t("legal.gate.point.noads")}</li>
          <li><Icon name="trash" size={18} /> {t("legal.gate.point.delete")}</li>
        </ul>
        <LegalLinks />
      </div>
      <p className="hint">{t("legal.gate.confirm")}</p>
      {error && <p className="error" role="alert">{error}</p>}
      <button className="btn btn-primary btn-big" disabled={sending} onClick={accept}>
        {t("legal.gate.accept")}
      </button>
    </section>
  );
}
