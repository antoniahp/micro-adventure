// Loads Google's own "Sign in with Google" script and renders its button. We never see a password:
// Google gives back a signed credential (an id_token), which the server checks before trusting it.
// Without a client id configured, callers get null and show the feature as unavailable instead of
// loading a script that can only fail.

declare global {
  interface Window {
    google?: {
      accounts: {
        id: {
          initialize(config: { client_id: string; callback: (response: { credential: string }) => void }): void;
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

// Renders Google's own button inside `container` and resolves once with the credential when the
// person picks an account, or rejects if the script can't load. Call it again to show it once more.
export async function renderGoogleSignIn(container: HTMLElement, lang: "es" | "en"): Promise<string> {
  if (!CLIENT_ID) throw new Error("Google sign-in is not configured");
  await loadScript();
  return new Promise((resolve, reject) => {
    try {
      window.google!.accounts.id.initialize({
        client_id: CLIENT_ID,
        callback: (response) => resolve(response.credential),
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
    } catch (e) {
      reject(e as Error);
    }
  });
}
