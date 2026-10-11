import { useEffect, useState } from "react";
import Icon from "./components/Icon";
import Logo from "./components/Logo";
import Tour from "./components/Tour";
import { markTourSeen, onToursRestarted, tourSeen } from "./components/tourStorage";
import { LANGUAGES, useI18n } from "./i18n";
import { currentWalk } from "./storage";
import DashboardScreen from "./screens/DashboardScreen";
import NotebookScreen from "./screens/NotebookScreen";
import RemindersScreen from "./screens/RemindersScreen";
import SettingsScreen from "./screens/SettingsScreen";
import StartScreen from "./screens/StartScreen";
import WalkScreen from "./screens/WalkScreen";

type Tab = "walk" | "dashboard" | "notebook" | "reminders" | "settings";

export default function App() {
  const { lang, setLang, t } = useI18n();
  // State = data that, when it changes, makes React redraw the screen.
  const [tab, setTab] = useState<Tab>("walk");
  const [walkId, setWalkId] = useState<string | null>(currentWalk.get());
  // The first time the app opens, a few bubbles say what each tab at the bottom is for.
  const [appTour, setAppTour] = useState(false);

  useEffect(() => {
    const timer = window.setTimeout(() => setAppTour(!tourSeen("app")), 600); // let the first screen settle
    const stop = onToursRestarted(() => setAppTour(true));
    return () => {
      window.clearTimeout(timer);
      stop();
    };
  }, []);

  function closeAppTour() {
    markTourSeen("app");
    setAppTour(false);
  }

  function startedWalk(id: string) {
    currentWalk.set(id);
    setWalkId(id);
  }

  function finishedWalk() {
    currentWalk.clear();
    setWalkId(null);
  }

  return (
    <div className="app">
      <header className="topbar">
        <Logo size={34} />
        <h1>MicroAdventures</h1>
        <div className="lang" role="group" aria-label={t("app.language")}>
          {LANGUAGES.map((code) => (
            <button key={code} aria-pressed={lang === code} lang={code} onClick={() => setLang(code)}>
              {code.toUpperCase()}
            </button>
          ))}
        </div>
      </header>

      <main>
        {tab === "dashboard" && <DashboardScreen />}
        {tab === "notebook" && <NotebookScreen onStartWalk={() => setTab("walk")} />}
        {tab === "reminders" && <RemindersScreen />}
        {tab === "settings" && <SettingsScreen />}
        {tab === "walk" && !walkId && <StartScreen onStarted={startedWalk} />}
        {tab === "walk" && walkId && (
          <WalkScreen walkId={walkId} onFinished={finishedWalk} onOpenNotebook={() => setTab("notebook")} />
        )}
      </main>

      <nav className="tabs">
        <button data-tour="tab-walk" className={tab === "walk" ? "active" : ""} onClick={() => setTab("walk")}>
          <Icon name="pin" size={22} /> {t("app.tabWalk")}
        </button>
        <button data-tour="tab-dashboard" className={tab === "dashboard" ? "active" : ""} onClick={() => setTab("dashboard")}>
          <Icon name="chart" size={22} /> {t("app.tabDashboard")}
        </button>
        <button data-tour="tab-notebook" className={tab === "notebook" ? "active" : ""} onClick={() => setTab("notebook")}>
          <Icon name="book" size={22} /> {t("app.tabNotebook")}
        </button>
        <button data-tour="tab-reminders" className={tab === "reminders" ? "active" : ""} onClick={() => setTab("reminders")}>
          <Icon name="bell" size={22} /> {t("app.tabReminders")}
        </button>
        <button data-tour="tab-settings" className={tab === "settings" ? "active" : ""} onClick={() => setTab("settings")}>
          <Icon name="user" size={22} /> {t("app.tabSettings")}
        </button>
      </nav>

      {appTour && (
        <Tour
          onDone={closeAppTour}
          steps={(["walk", "dashboard", "notebook", "reminders", "settings"] as const).map((name) => ({
            target: `tab-${name}`,
            title: t(`tour.app.${name}.title`),
            text: t(`tour.app.${name}.text`),
          }))}
        />
      )}
    </div>
  );
}
