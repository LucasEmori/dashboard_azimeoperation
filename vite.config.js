import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// Dev: `python app.py` (FastAPI, porta 8501) + `npm run dev` (Vite, porta 5173).
// Vite proxya /api e /data.json pro backend local.
// Prod: FastAPI serve dist/ + API na mesma porta (Railway $PORT).
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    host: true,
    proxy: {
      '/api': 'http://127.0.0.1:8501',
      '/data.json': 'http://127.0.0.1:8501'
    }
  },
  build: { outDir: 'dist' }
})