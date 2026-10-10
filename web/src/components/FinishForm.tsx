import { useState } from "react";
import { useI18n } from "../i18n";
import Icon from "./Icon";
import { CAN_RECORD, useVoiceNote } from "./useVoiceNote";

const MAX_DIARY = 2000; // same limit as the backend (MAX_DIARY_LENGTH)

export type FinishData = { walkedMinutes: number | null; distanceKm: number | null; diary: string };

type Props = { busy: boolean; error: string; skipLabel: string; initial?: FinishData; onSubmit: (data: FinishData) => void; onSkip: () => void };

// "5,2" and "5.2" are both km. Anything that is not a positive number counts as empty.
function toNumber(text: string): number | null {
  const value = Number(text.trim().replace(",", "."));
  return text.trim() !== "" && Number.isFinite(value) && value > 0 ? value : null;
}

// The end of the walk: the real time, the distance and the story of the walk, all optional.
export default function FinishForm({ busy, error, skipLabel, initial, onSubmit, onSkip }: Props) {
  const { t } = useI18n();
  const [minutes, setMinutes] = useState(initial?.walkedMinutes ? String(initial.walkedMinutes) : "");
  const [km, setKm] = useState(initial?.distanceKm ? String(initial.distanceKm).replace(".", ",") : "");
  const [diary, setDiary] = useState(initial?.diary ?? "");
  const voice = useVoiceNote((spoken) => setDiary((current) => (current ? `${current} ${spoken}` : spoken)));

  const [problem, setProblem] = useState("");
  const disabled = busy || voice.recording || voice.transcribing;

  function submit() {
    const walkedMinutes = toNumber(minutes);
    const distance = toNumber(km);
    if (walkedMinutes !== null && (walkedMinutes < 1 || walkedMinutes > 720)) return setProblem(t("finish.badMinutes"));
    if (distance !== null && distance > 200) return setProblem(t("finish.badKm"));
    setProblem("");
    onSubmit({
      walkedMinutes: walkedMinutes === null ? null : Math.round(walkedMinutes),
      distanceKm: distance,
      diary: diary.trim(),
    });
  }

  return (
    <div className="finish-form">
      <h3>{t("finish.title")}</h3>
      <p className="hint">{t("finish.intro")}</p>

      <div className="finish-numbers">
        <div className="field">
          <label htmlFor="walked-minutes">{t("finish.minutes")}</label>
          <input id="walked-minutes" type="number" inputMode="numeric" min={1} max={720} value={minutes} onChange={(e) => setMinutes(e.target.value)} placeholder="40" />
        </div>
        <div className="field">
          <label htmlFor="walked-km">{t("finish.km")}</label>
          <input id="walked-km" type="text" inputMode="decimal" value={km} onChange={(e) => setKm(e.target.value)} placeholder="3,5" />
        </div>
      </div>

      <div className="field">
        <label htmlFor="walk-diary">{t("finish.diary")}</label>
        <textarea
          id="walk-diary"
          rows={5}
          maxLength={MAX_DIARY}
          value={diary}
          disabled={voice.transcribing}
          onChange={(e) => setDiary(e.target.value)}
          placeholder={voice.transcribing ? t("story.transcribing") : t("finish.diaryPlaceholder")}
        />
        <p className="hint"><span className="count">{diary.length}/{MAX_DIARY}</span></p>
      </div>

      {(problem || voice.error || error) && <p className="error" role="alert">{problem || voice.error || error}</p>}

      <div className="story-actions">
        {CAN_RECORD &&
          (voice.recording ? (
            <button className="btn btn-record recording" onClick={voice.stop}>
              <Icon name="stop" size={18} /> {t("story.stop", { n: voice.seconds })}
            </button>
          ) : (
            <button className="btn btn-secondary" onClick={voice.start} disabled={voice.transcribing || busy}>
              <Icon name="mic" size={18} /> {t("story.record")}
            </button>
          ))}
        <button className="btn btn-primary" disabled={disabled} onClick={submit}>
          {busy ? t("story.saving") : t("finish.save")}
        </button>
        <button className="btn btn-link" disabled={busy} onClick={onSkip}>{skipLabel}</button>
      </div>
    </div>
  );
}
