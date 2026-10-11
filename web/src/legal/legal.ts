// The privacy and terms pages: plain HTML with both languages in it. This shows the one the person uses in the
// app (or their browser's), and the ES/EN switch changes it and remembers it, exactly like the app does.
import "@fontsource-variable/bricolage-grotesque/opsz.css";
import "./legal.css";

type Lang = "es" | "en";

function saved(): Lang | null {
  try {
    const lang = localStorage.getItem("lang");
    return lang === "es" || lang === "en" ? lang : null;
  } catch {
    return null;
  }
}

function show(lang: Lang) {
  document.documentElement.lang = lang;
  document.documentElement.dataset.show = lang;
  document.querySelectorAll<HTMLButtonElement>("[data-lang]").forEach((button) => {
    button.setAttribute("aria-pressed", String(button.dataset.lang === lang));
  });
  const heading = document.querySelector(`article[lang="${lang}"] h1`)?.textContent;
  if (heading) document.title = `${heading} · MicroAdventures`;
}

show(saved() ?? (navigator.language?.toLowerCase().startsWith("es") ? "es" : "en"));

document.querySelectorAll<HTMLButtonElement>("[data-lang]").forEach((button) => {
  button.addEventListener("click", () => {
    const lang = button.dataset.lang as Lang;
    show(lang);
    try {
      localStorage.setItem("lang", lang);
    } catch {
      /* the choice just won't be remembered */
    }
  });
});

// On a phone the tables become one card per row: each cell carries its column's name so it still reads.
document.querySelectorAll("table").forEach((table) => {
  const headings = [...table.querySelectorAll("thead th")].map((th) => th.textContent ?? "");
  table.querySelectorAll("tbody tr").forEach((row) => {
    [...row.children].forEach((cell, i) => cell.setAttribute("data-label", headings[i] ?? ""));
  });
});
