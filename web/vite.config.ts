import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";

// In development the browser calls /api on the Vite server (port 5173),
// and Vite forwards it to Django (port 8000). That way we don't need CORS.
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: { "/api": "http://localhost:8000" },
  },
});
