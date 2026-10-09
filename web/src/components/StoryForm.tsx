import { useState } from "react";
import { useI18n } from "../i18n";
import Icon from "./Icon";
import { CAN_RECORD, useVoiceNote } from "./useVoiceNote";

const MIN_LENGTH = 10; // same minimum as the backend (MIN_STORY_LENGTH)

type Props = { busy: boolean; onSubmit: (story: string) => void; onCancel: () => void };

// Where the person tells the challenge: they write it, or record a voice note that
// is turned into text they can still edit before sending.
export default function StoryForm({ busy, onSubmit, onCancel }: Props) {
  const { t } = useI18n();
  const [text, setText] = useState("");
  const voice = useVoiceNote((spoken) => setText((current) => (current ? `${current} ${spoken}` : spoken)));

  const ready = text.trim().length >= MIN_LENGTH && !voice.recording && !voice.transcribing && !busy;

  return (
    <div className="story-form">
      <textarea
        rows={3}
        value={text}
        maxLength={1000}
        disabled={voice.transcribing}
        onChange={(e) => setText(e.target.value)}
        placeholder={voice.transcribing ? t("story.transcribing") : t("story.placeholder")}
        aria-label={t("story.aria")}
      />
      {voice.error && <p className="error" role="alert">{voice.error}</p>}
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
        <button className="btn btn-primary" disabled={!ready} onClick={() => onSubmit(text.trim())}>
          {busy ? t("story.saving") : t("story.send")}
        </button>
        <button className="btn btn-link" onClick={onCancel} disabled={busy}>{t("story.cancel")}</button>
      </div>
      {text.trim().length < MIN_LENGTH && <p className="hint">{t("story.minChars", { n: MIN_LENGTH })}</p>}
    </div>
  );
}
