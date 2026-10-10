import Icon from "./Icon";
import { useI18n, type TextKey } from "../i18n";
import type { WalkContext } from "../types";

function formatLight(minutes: number) {
  const hours = Math.floor(minutes / 60), rest = minutes % 60;
  if (!hours) return `${rest} min`;
  return rest ? `${hours} h ${rest} min` : `${hours} h`;
}

function clock(iso: string) {
  return new Date(iso).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }); // shown in the time of the phone, which is where the person is
}

export type ContextState =
  | { status: "idle" }
  | { status: "loading" }
  | { status: "ready"; context: WalkContext }
  | { status: "failed"; reason: "denied" | "unavailable" };

// The weather and the light before the walk, and what they change in it.
export default function ContextCard({ state, onAsk }: { state: ContextState; onAsk: () => void }) {
  const { t } = useI18n();

  if (state.status === "idle") {
    return (
      <div className="context">
        <p className="context-line"><Icon name="sun" size={20} /> {t("context.ask")}</p>
        <p className="hint">{t("context.hint")}</p>
        <button className="btn btn-secondary" onClick={onAsk}><Icon name="pin" size={18} /> {t("context.button")}</button>
      </div>
    );
  }
  if (state.status === "loading") return <div className="context" role="status"><p className="hint">{t("context.loading")}</p></div>;
  if (state.status === "failed") {
    return (
      <div className="context">
        <p className="hint" role="status">{t(state.reason === "denied" ? "context.denied" : "context.unavailable")}</p>
        <button className="btn btn-link left" onClick={onAsk}>{t("context.retry")}</button>
      </div>
    );
  }

  const { context } = state;
  const { conditions } = context;
  const icon = conditions.dark ? "moon" : context.sky === "clear" ? "sun" : context.sky === "cloudy" || context.sky === "fog" ? "cloud" : "rain";
  return (
    <div className="context" role="status">
      <div className="context-head">
        <span className="context-icon"><Icon name={icon} size={30} /></span>
        <strong className="context-temp">{Math.round(context.temperature_c)} °C</strong>
        <span className="context-sky">{t(`sky.${context.sky}` as TextKey)}</span>
      </div>
      <p className="context-line">
        <Icon name="clock" size={18} />
        {conditions.dark ? t("context.dark") : t("context.light", { light: formatLight(context.minutes_of_light), time: clock(context.sunset) })}
      </p>
      {conditions.storm ? (
        <p className="context-note">{t("context.storm")}</p>
      ) : (
        <>
          {conditions.dark && <p className="context-note">{t("context.safe")}</p>}
          {conditions.rain && <p className="context-note">{t("context.rain")}</p>}
        </>
      )}
      {conditions.cold && <p className="context-note">{t("context.cold")}</p>}
      {conditions.hot && <p className="context-note">{t("context.hot")}</p>}
    </div>
  );
}
