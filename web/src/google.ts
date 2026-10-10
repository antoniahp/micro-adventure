// Loads Google's own "Sign in with Google" script and renders its button. We never see a password:
// Google gives back a signed credential (an id_token), which the server checks before trusting it.
// Without a client id configured, callers get null and show the feature as unavailable instead of
// loading a script that can only fail.

declare global {
  interface Window {
    google?: {
      accounts: {
        id: {
          initialize(config: {
            client_id: string;
            callback?: (response: { credential: string }) => void;
            ux_mode?: "popup" | "redirect";
            login_uri?: string;
          }): void;
          renderButton(parent: HTMLElement, options: Record<string, string | number>): void;
        };
      };
    };
  }
}

const CLIENT_ID = import.meta.env.VITE_GOOGLE_CLIENT_ID as string | undefined;

let loading: Promise<void> | null = null;

function loadScript(): Promise<void> {
  loading ??= new Promise((resolve, reject) => {
    if (window.google?.accounts?.id) return resolve();
    const script = document.createElement("script");
    script.src = "https://accounts.google.com/gsi/client";
    script.async = true;
    script.defer = true;
    script.onload = () => resolve();
    script.onerror = () => reject(new Error("could not load accounts.google.com"));
    document.head.appendChild(script);
  });
  return loading;
}

export const googleSignInAvailable = Boolean(CLIENT_ID);

// Google's default "popup" mode (window.open) is unreliable inside an installed PWA: the popup can
// come up blank and stuck instead of showing the account picker. Redirect mode avoids that - the whole
// page navigates to Google and back, the same way in an installed app as in an ordinary browser tab -
// so the button always uses it, not just when installed.
const REDIRECT_URI = `${window.location.origin}/google/redirect-login`;

// Renders Google's own button inside `container`. The person picking an account navigates away and
// back; use consumePendingGoogleCredential() on the next page load to pick up the result.
export async function renderGoogleSignIn(container: HTMLElement, lang: "es" | "en"): Promise<void> {
  if (!CLIENT_ID) throw new Error("Google sign-in is not configured");
  await loadScript();
  window.google!.accounts.id.initialize({
    client_id: CLIENT_ID,
    ux_mode: "redirect",
    login_uri: REDIRECT_URI,
  });
  container.innerHTML = "";
  window.google!.accounts.id.renderButton(container, {
    type: "standard",
    theme: "outline",
    size: "large",
    shape: "pill",
    text: "continue_with",
    locale: lang,
    width: 280,
  });
}

// Reads back the credential the redirect left in the URL fragment (never sent to any server) and
// clears it, so a later reload of the same page doesn't try to link it again. null when there is none.
export function consumePendingGoogleCredential(): string | null {
  const match = /(?:^|&)google_credential=([^&]+)/.exec(window.location.hash.slice(1));
  if (!match) return null;
  history.replaceState(null, "", window.location.pathname + window.location.search);
  return decodeURIComponent(match[1]);
}
