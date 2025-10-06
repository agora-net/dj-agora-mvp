import { defineConfig } from 'vite'
import tailwindcss from '@tailwindcss/vite'
import react from '@vitejs/plugin-react-swc'

// https://vite.dev/config/
export default defineConfig({
  base: "/static/",
  plugins: [react(), tailwindcss()],
  server: {
    allowedHosts: [".local.agora.gdn"],
    host: true,
  },
  build: {
    outDir: "dist",
    manifest: "manifest.json",
    rollupOptions: {
      input: {
        tailwind: "src/tailwind.css",
        confetti: "src/confetti.ts",
        themeChange: "src/theme-change.ts",
        icons: "src/icons.ts",
      },
    },
  },
})
