import { useEffect, useState } from "react";
import { completeChallenge, finishWalk, getWalk, MAX_SWAPS_PER_WALK, swapChallenge } from "../api";
import FinishForm, { type FinishData } from "../components/FinishForm";
import Icon from "../components/Icon";
import Loader from "../components/Loader";
import StoryForm from "../components/StoryForm";
import { useI18n, type TextKey } from "../i18n";
import type { Challenge, Walk } from "../types";
import { CATEGORIES, FALLBACK_CATEGORY } from "../ui";

type Props = { walkId: string; onFinished: () => void; onOpenNotebook: () => void };

export default function WalkScreen({ walkId, onFinished, onOpenNotebook }: Props) {
  const { t, lang } = useI18n();
  const [walk, setWalk] = useState<Walk | null>(null);
  const [loadError, setLoadError] = useState("");
  const [busyId, setBusyId] = useState<string | null>(null);
  const [errors, setErrors] = useState<Record<string, string>>({}); // one message per challenge
  const [photos, setPhotos] = useState<Record<string, string>>({}); // preview of each photo sent
  const [justDone, setJustDone] = useState<string | null>(null); // which entry to animate
  const [telling, setTelling] = useState<string | null>(null); // which entry has its story form open
  // Three screens: the challenges, the "walk complete" page, and the page where the person tells the walk.
  const [view, setView] = useState<"challenges" | "done" | "tell">("challenges");
  const [finishBusy, setFinishBusy] = useState(false);
  const [finishError, setFinishError] = useState("");

  // useEffect runs after the screen is drawn. Here: load the walk once per walkId.
  useEffect(() => {
    getWalk(walkId)
      .then((loaded) => {
        setWalk(loaded);
        if (loaded.challenges.every((c) => c.status === "completed")) setView("done"); // coming back to a finished walk
      })
      .catch((e: Error) => setLoadError(e.message));
  }, [walkId]);

  // Each screen starts at the top.
  useEffect(() => {
    window.scrollTo(0, 0);
  }, [view]);

  // Runs an action on one challenge, then reloads the walk to show the new state.
  async function act(challenge: Challenge, action: () => Promise<void>, photo?: File) {
    setBusyId(challenge.id);
    setErrors((current) => ({ ...current, [challenge.id]: "" }));
    try {
      await action();
      setTelling(null);
      if (photo) setPhotos((current) => ({ ...current, [challenge.id]: URL.createObjectURL(photo) }));
      const updated = await getWalk(walkId);
      setWalk(updated);
      setJustDone(challenge.id);
      if (updated.challenges.every((c) => c.status === "completed")) setView("done");
    } catch (e) {
      setErrors((current) => ({ ...current, [challenge.id]: (e as Error).message }));
    } finally {
      setBusyId(null);
    }
  }

  async function saveFinish(data: FinishData) {
    setFinishBusy(true);
    setFinishError("");
    try {
      await finishWalk(walkId, data);
      setWalk(await getWalk(walkId));
      setView("done");
    } catch (e) {
      setFinishError((e as Error).message);
    } finally {
      setFinishBusy(false);
    }
  }

  if (loadError) {
    return (
      <section>
        <p className="error" role="alert">{loadError}</p>
        <button className="btn btn-secondary" onClick={onFinished}>{t("walk.startAnother")}</button>
      </section>
    );
  }
  if (!walk) return <Loader title={t("walk.opening")} />;

  const swapsLeft = MAX_SWAPS_PER_WALK - walk.swaps_used;
  const doneCount = walk.challenges.filter((c) => c.status === "completed").length;
  const total = walk.challenges.length;
  const allDone = doneCount === total;
  const told = walk.finished_at !== null;
  const decimal = lang === "es" ? "," : ".";
  const stats = [
    { value: `${doneCount}/${total}`, label: t("done.challenges") },
    { value: walk.walked_minutes ? String(walk.walked_minutes) : "–", label: t("done.minutes") },
    { value: walk.distance_km ? String(walk.distance_km).replace(".", decimal) : "–", label: t("done.km") },
  ];

  if (view === "tell") {
    return (
      <section>
        <FinishForm
          initial={told ? { walkedMinutes: walk.walked_minutes, distanceKm: walk.distance_km, diary: walk.diary } : undefined}
          busy={finishBusy}
          error={finishError}
          skipLabel={told ? t("story.cancel") : allDone ? t("finish.later") : t("finish.leave")}
          onSubmit={saveFinish}
          onSkip={() => (told || allDone ? setView("done") : onFinished())}
        />
      </section>
    );
  }

  if (view === "done") {
    return (
      <section className="done-page">
        <span className="stamp big" aria-hidden="true"><Icon name="check" size={34} /></span>
        <div>
          <h2>{allDone ? t("walk.finishedTitle") : t("walk.endedTitle")}</h2>
          <p className="hint">{allDone && walk.swaps_used === 0 ? t("walk.finishedPerfect") : t("walk.finishedNormal")}</p>
        </div>

        <dl className="done-stats">
          {stats.map((stat) => (
            <div key={stat.label} className={stat.value === "–" ? "stat empty" : "stat"}>
              <dd>{stat.value}</dd>
              <dt>{stat.label}</dt>
            </div>
          ))}
        </dl>

        {walk.diary ? (
          <blockquote className="entry-story done-story">{walk.diary}</blockquote>
        ) : (
          <p className="hint">{t("done.storyPrompt")}</p>
        )}

        <div className="done-actions">
          <button className="btn btn-primary btn-big" onClick={() => setView("tell")}>{told ? t("walk.editTold") : t("walk.tellWalk")}</button>
          <div className="done-links">
            <button className="btn btn-link" onClick={onOpenNotebook}>{t("walk.seeNotebook")}</button>
            <button className="btn btn-link" onClick={onFinished}>{t("walk.newWalk")}</button>
          </div>
          <button className="btn btn-link small" onClick={() => setView("challenges")}>{t("walk.backToChallenges")}</button>
        </div>
      </section>
    );
  }

  return (
    <section>
      <h2>{t("walk.title")}</h2>
      {walk.language !== lang && <p className="hint" role="status">{t("walk.languageNote")}</p>}
      <div className="progress">
        <div className="progress-bar" role="progressbar" aria-valuemin={0} aria-valuemax={total} aria-valuenow={doneCount}>
          {walk.challenges.map((c) => (
            <span key={c.id} className={c.status === "completed" ? "full" : ""} style={{ "--c": (CATEGORIES[c.category] ?? FALLBACK_CATEGORY).color } as React.CSSProperties} />
          ))}
        </div>
        <span className="progress-text">{t("walk.progress", { done: doneCount, total })}</span>
      </div>

      <ol className="entries">
        {walk.challenges.map((c) => {
          const category = CATEGORIES[c.category] ?? FALLBACK_CATEGORY;
          const done = c.status === "completed";
          const busy = busyId === c.id;
          return (
            <li key={c.id} className={done ? "entry done" : "entry"} style={{ "--c": category.color, "--tint": category.tint, "--ink-c": category.ink, "--on": category.color === "#FFB300" ? "#1d1b3a" : "#fff" } as React.CSSProperties}>
              <span className={done && justDone === c.id ? "badge stamp" : "badge"} aria-hidden="true">
                <Icon name={done ? "check" : category.icon} size={22} />
              </span>
              <div className="entry-body">
                <p className="entry-category">
                  {t(`cat.${CATEGORIES[c.category] ? c.category : "fallback"}` as TextKey)}
                  <span
                    className={c.source === "template" ? "source-dot" : "source-dot model"}
                    role="img"
                    title={c.source === "template" ? t("walk.sourceTemplate") : t("walk.sourceModel", { model: c.source })}
                    aria-label={c.source === "template" ? t("walk.sourceTemplate") : t("walk.sourceModel", { model: c.source })}
                  />
                </p>
                <p className="entry-text">{c.text}</p>

                {c.story && <blockquote className="entry-story">{c.story}</blockquote>}
                {photos[c.id] && <img className="entry-photo" src={photos[c.id]} alt={t("walk.photoAlt")} />}
                {errors[c.id] && <p className="error" role="alert">{errors[c.id]}</p>}

                {!done && telling === c.id && (
                  <StoryForm busy={busy} onCancel={() => setTelling(null)} onSubmit={(story) => act(c, () => completeChallenge(walk.id, c.id, { story }))} />
                )}

                {!done && telling !== c.id && (
                  <>
                    {!c.accepts_photo && <p className="hint">{t("walk.noPeoplePhotos")}</p>}
                    <div className="entry-actions">
                      <button className="btn btn-primary" disabled={busy} onClick={() => setTelling(c.id)}>
                        <Icon name="pen" size={18} /> {t("walk.tell")}
                      </button>
                      {c.accepts_photo && (
                        <label className={busy ? "btn btn-secondary disabled" : "btn btn-secondary"}>
                          <Icon name="camera" size={18} />
                          {busy ? t("walk.photoChecking") : errors[c.id] ? t("walk.photoAgain") : t("walk.photo")}
                          <input
                            type="file"
                            accept="image/*"
                            capture="environment"
                            hidden
                            disabled={busy}
                            onChange={(e) => {
                              const photo = e.target.files?.[0];
                              e.target.value = ""; // lets the player pick the same file again after an error
                              if (photo) act(c, () => completeChallenge(walk.id, c.id, { photo }), photo);
                            }}
                          />
                        </label>
                      )}
                      <button className="btn btn-link" disabled={busy || swapsLeft === 0} onClick={() => act(c, () => swapChallenge(walk.id, c.id))}>
                        {swapsLeft === 0 ? t("walk.noSwaps") : t("walk.swap", { n: swapsLeft })}
                      </button>
                    </div>
                  </>
                )}
              </div>
            </li>
          );
        })}
      </ol>

      {allDone ? (
        <button className="btn btn-link left" onClick={() => setView("done")}>{t("walk.seeSummary")}</button>
      ) : (
        <>
          <p className="hint">{t("walk.swapWarning")}</p>
          <button className="btn btn-link left" onClick={() => setView(told ? "done" : "tell")}>{t("walk.finish")}</button>
        </>
      )}
    </section>
  );
}
