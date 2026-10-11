// Whether this person has accepted the current privacy policy and terms, shared by every screen that keeps
// something about them (starting a walk, saving a name, connecting Google or Telegram). Each of those shows a
// short notice next to its button until the first acceptance; tapping one of them, with the notice in view, is the
// acceptance, recorded (version and time) by the server before anything else is sent.
import { useEffect, useState } from "react";
import { acceptLegal, getAccount } from "./api";
import { getUserId } from "./storage";

let accepted: boolean | null = null; // null: not known yet
let loading: Promise<void> | null = null;
const listeners = new Set<() => void>();

function set(value: boolean) {
  accepted = value;
  listeners.forEach((listener) => listener());
}

function load(): Promise<void> {
  loading ??= getAccount(getUserId())
    .then((account) => set(account.legal_accepted))
    .catch(() => {
      loading = null; // offline: asked again next time a screen needs it
    });
  return loading;
}

// true when the notice must show. While unknown it stays hidden, so it never flashes for people who accepted long ago.
export function useLegalNoticeNeeded(): boolean {
  const [, redraw] = useState(0);
  useEffect(() => {
    const listener = () => redraw((n) => n + 1);
    listeners.add(listener);
    load();
    return () => {
      listeners.delete(listener);
    };
  }, []);
  return accepted === false;
}

// Called by the buttons that carry the notice, before they send anything.
export async function acceptLegalIfNeeded(): Promise<void> {
  if (accepted === null) await load();
  if (accepted === false) {
    await acceptLegal(getUserId());
    set(true);
  }
}

