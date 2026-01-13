import { defineConfig } from "vite";
import react from "@vitejs/plugin-react-swc";
import path from "path";

// https://vitejs.dev/config/
export default defineConfig(({ mode }) => ({
  server: {
    host: "::",
    port: 5173, // Puerto diferente al backend (8080)
    proxy: {
      // Proxy para las rutas de API al backend
      "/ask": {
        target: "http://localhost:8080",
        changeOrigin: true,
      },
      "/health": {
        target: "http://localhost:8080",
        changeOrigin: true,
      },
      "/schema": {
        target: "http://localhost:8080",
        changeOrigin: true,
      },
      "/metrics": {
        target: "http://localhost:8080",
        changeOrigin: true,
      },
      "/logs": {
        target: "http://localhost:8080",
        changeOrigin: true,
      },
    },
  },
  plugins: [react()],
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
}));
