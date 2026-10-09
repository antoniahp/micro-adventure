import { useEffect, useRef, useState } from "react";
import { transcribe } from "../api";
import { useI18n } from "../i18n";

export const CAN_RECORD = typeof navigator !== "undefined" && !!navigator.mediaDevices?.getUserMedia && typeof MediaRecorder !== "undefined";

// Records a voice note and hands its text to onText. The person can still edit that text before sending it.
export function useVoiceNote(onText: (spoken: string) => void) {
  const { t } = useI18n();
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
  useEffect(() => () => recorder.current?.stream.getTracks().forEach((track) => track.stop()), []);

  async function start() {
    setError("");
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mediaRecorder = new MediaRecorder(stream);
      chunks.current = [];
      mediaRecorder.ondataavailable = (e) => chunks.current.push(e.data);
      mediaRecorder.onstop = async () => {
        stream.getTracks().forEach((track) => track.stop());
        setTranscribing(true);
        try {
          const voice = new Blob(chunks.current, { type: mediaRecorder.mimeType || "audio/webm" });
          onText(await transcribe(voice));
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

  function stop() {
    recorder.current?.stop();
    setRecording(false);
  }

  return { recording, seconds, transcribing, error, start, stop };
}
