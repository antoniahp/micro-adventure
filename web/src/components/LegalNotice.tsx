import { useI18n, type TextKey } from "../i18n";

// "By starting, you accept the terms of use and confirm you've read the privacy policy." Shown right next to the
// button whose tap counts as the acceptance; `lead` is the first words, which name that button's action.
export default function LegalNotice({ lead }: { lead: TextKey }) {
  const { t } = useI18n();
  return (
    <p className="legal-notice">
      {t(lead)}
      <a href="/terms.html">{t("legal.notice.terms")}</a>
      {t("legal.notice.middle")}
      <a href="/privacy.html">{t("legal.notice.privacy")}</a>
      {t("legal.notice.after")}
    </p>
  );
}
