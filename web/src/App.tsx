import { useState } from "react";
import Icon from "./components/Icon";
import Logo from "./components/Logo";
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
        <button className={tab === "walk" ? "active" : ""} onClick={() => setTab("walk")}>
          <Icon name="pin" size={22} /> {t("app.tabWalk")}
        </button>
        <button className={tab === "dashboard" ? "active" : ""} onClick={() => setTab("dashboard")}>
          <Icon name="chart" size={22} /> {t("app.tabDashboard")}
        </button>
        <button className={tab === "notebook" ? "active" : ""} onClick={() => setTab("notebook")}>
          <Icon name="book" size={22} /> {t("app.tabNotebook")}
        </button>
        <button className={tab === "reminders" ? "active" : ""} onClick={() => setTab("reminders")}>
          <Icon name="bell" size={22} /> {t("app.tabReminders")}
        </button>
        <button className={tab === "settings" ? "active" : ""} onClick={() => setTab("settings")}>
          <Icon name="user" size={22} /> {t("app.tabSettings")}
        </button>
      </nav>
    </div>
  );
}
