import { useState } from "react";
import Icon from "./components/Icon";
import { currentWalk } from "./storage";
import NotebookScreen from "./screens/NotebookScreen";
import StartScreen from "./screens/StartScreen";
import WalkScreen from "./screens/WalkScreen";

type Tab = "walk" | "notebook";

export default function App() {
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
        <Icon name="compass" size={22} />
        <h1>MicroAdventures</h1>
      </header>

      <main>
        {tab === "notebook" && <NotebookScreen onStartWalk={() => setTab("walk")} />}
        {tab === "walk" && !walkId && <StartScreen onStarted={startedWalk} />}
        {tab === "walk" && walkId && (
          <WalkScreen walkId={walkId} onFinished={finishedWalk} onOpenNotebook={() => setTab("notebook")} />
        )}
      </main>

      <nav className="tabs">
        <button className={tab === "walk" ? "active" : ""} onClick={() => setTab("walk")}>
          <Icon name="pin" size={22} /> Paseo
        </button>
        <button className={tab === "notebook" ? "active" : ""} onClick={() => setTab("notebook")}>
          <Icon name="book" size={22} /> Cuaderno
        </button>
      </nav>
    </div>
  );
}
