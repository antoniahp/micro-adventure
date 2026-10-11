import { useI18n } from "../i18n";

// The privacy policy and the terms are their own pages (privacy.html, terms.html): readable by anyone,
// with or without the app, and linkable from Google's consent screen.
export default function LegalLinks() {
  const { t } = useI18n();
  return (
    <p className="legal-links">
      <a href="/privacy.html">{t("legal.privacy")}</a>
      <span aria-hidden="true">·</span>
      <a href="/terms.html">{t("legal.terms")}</a>
    </p>
  );
}
