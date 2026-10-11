import React from "react";
import ReactDOM from "react-dom/client";
import App from "./App";
import { I18nProvider } from "./i18n";
// The typeface is served from our own server: no request to Google Fonts, and so no visitor IP sent there.
import "@fontsource-variable/bricolage-grotesque/opsz.css";
import "./styles.css";
import { registerServiceWorker } from "./pwa";
import { ensureSession } from "./session";

registerServiceWorker();

// The session is ready before the first screen asks for anything. If the server cannot be reached now,
// the app opens anyway and each request tries again.
ensureSession()
  .catch(() => false)
  .then(() =>
    ReactDOM.createRoot(document.getElementById("root")!).render(
      <React.StrictMode>
        <I18nProvider>
          <App />
        </I18nProvider>
      </React.StrictMode>,
    ),
  );
