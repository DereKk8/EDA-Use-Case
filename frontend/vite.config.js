import { defineConfig } from 'vite'
import { svelte } from '@sveltejs/vite-plugin-svelte'

export default defineConfig({
  plugins: [svelte()],
  server: {
    port: 5173,
    host: '0.0.0.0',
    proxy: {
      '/pedidos':   'http://localhost:8000',
      '/productos': 'http://localhost:8000',
    }
  }
})
