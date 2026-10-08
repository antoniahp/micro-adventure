import { useEffect, useRef, useState } from "react";
import { transcribe } from "../api";
import { useI18n } from "../i18n";
import Icon from "./Icon";

const MIN_LENGTH = 10; // same minimum as the backend (MIN_STORY_LENGTH)
const CAN_RECORD = typeof navigator !== "undefined" && !!navigator.mediaDevices?.getUserMedia && typeof MediaRecorder !== "undefined";

type Props = { busy: boolean; onSubmit: (story: string) => void; onCancel: () => void };

// Where the person tells the challenge: they write it, or record a voice note that
// is turned into text they can still edit before sending.
export default function StoryForm({ busy, onSubmit, onCancel }: Props) {
  const { t } = useI18n();
  const [text, setText] = useState("");
  const [recording, setRecording] = useState(false);
  const [seconds, setSeconds] = useState(0);
  const [transcribing, setTranscribing] = useState(false);
  const [error, setError] = useState("");
  const recorder = useRef<MediaRecorder | null>(null);
  const chunks = useRef<Blob[]>([]);

  // Counts the seconds while recording.
  useEffect(() => {
    if (!recording) return;
    setSeconds(0);
    const timer = setInterval(() => setSeconds((s) => s + 1), 1000);
    return () => clearInterval(timer);
  }, [recording]);

  // Releases the microphone if the person leaves in the middle of a recording.
  useEffect(() => () => recorder.current?.stream.getTracks().forEach((t) => t.stop()), []);

  async function startRecording() {
    setError("");
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mediaRecorder = new MediaRecorder(stream);
      chunks.current = [];
      mediaRecorder.ondataavailable = (e) => chunks.current.push(e.data);
      mediaRecorder.onstop = async () => {
        stream.getTracks().forEach((t) => t.stop());
        setTranscribing(true);
        try {
          const voice = new Blob(chunks.current, { type: mediaRecorder.mimeType || "audio/webm" });
          const spoken = await transcribe(voice);
          setText((current) => (current ? `${current} ${spoken}` : spoken));
        } catch (e) {
          setError((e as Error).message);
        } finally {
          setTranscribing(false);
        }
      };
      mediaRecorder.start();
      recorder.current = mediaRecorder;
      setRecording(true);
    } catch {
      setError(t("story.micError"));
    }
  }

  function stopRecording() {
    recorder.current?.stop();
    setRecording(false);
  }

  const ready = text.trim().length >= MIN_LENGTH && !recording && !transcribing && !busy;

  return (
    <div className="story-form">
      <textarea
        rows={3}
        value={text}
        maxLength={1000}
        disabled={transcribing}
        onChange={(e) => setText(e.target.value)}
        placeholder={transcribing ? t("story.transcribing") : t("story.placeholder")}
        aria-label={t("story.aria")}
      />
      {error && <p className="error" role="alert">{error}</p>}
      <div className="story-actions">
        {CAN_RECORD &&
          (recording ? (
            <button className="btn btn-record recording" onClick={stopRecording}>
              <Icon name="stop" size={18} /> {t("story.stop", { n: seconds })}
            </button>
          ) : (
            <button className="btn btn-secondary" onClick={startRecording} disabled={transcribing || busy}>
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
