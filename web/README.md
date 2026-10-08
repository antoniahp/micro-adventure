# web

Web client for MicroAdventures: React + Vite + TypeScript, mobile-first. Challenges are drawn as stickers: completing one slaps it onto the page.

```bash
npm install
npm run dev      # http://localhost:5173
```

The backend must be running on port 8000 (`make run` in the repo root). Vite forwards `/api` to it (see `vite.config.ts`), so no CORS setup is needed.

## Where things are

| File | What it does |
| --- | --- |
| `src/main.tsx` | Entry point: mounts React |
| `src/i18n.tsx` | All the texts in Spanish and English, the language switch and `t()` |
| `src/sky.ts` | Sky colours, sun, moon and lamp for the hour on the device. Open the app with `?hour=21` to preview any hour |
| `src/App.tsx` | Tabs (walk / notebook) and which walk is active |
| `src/api.ts` | Every call to the backend |
| `src/types.ts` | Types that mirror the API JSON |
| `src/storage.ts` | Anonymous user id and current walk, kept in `localStorage` |
| `src/ui.ts` | Names, colours and icons for categories, moods, weather and stickers |
| `src/components/` | Small pieces: loader, animated logo, trail illustration (flying birds, drifting clouds, fireflies), icons, and `StoryForm` (write or record a voice note) |
| `src/screens/` | One file per screen: start, walk, notebook |
| `src/styles.css` | All styles |

## Next steps

- Install as an app (PWA manifest and service worker)
- Show the photo verdict message when a photo is rejected
