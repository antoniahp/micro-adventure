import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";

// In development the browser calls /api on the Vite server (port 5173),
// and Vite forwards it to Django (port 8000). That way we don't need CORS.
// Three pages (paths relative to this folder, where the build runs): the app, and the privacy and terms pages (plain HTML, readable without the app).
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: { "/api": "http://localhost:8000" },
  },
  build: {
    rollupOptions: {
      input: {
        app: "index.html",
        privacy: "privacy.html",
        terms: "terms.html",
      },
    },
  },
});
