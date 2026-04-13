import { defineConfig } from 'vite'
import { svelte } from '@sveltejs/vite-plugin-svelte'

const apiProxyTarget = process.env.VITE_API_PROXY_TARGET || 'http://backend-dev:8000'

export default defineConfig({
  plugins: [svelte()],
  server: {
    port: 5173,
    host: '0.0.0.0',
    proxy: {
      '/pedidos': { target: apiProxyTarget, changeOrigin: true },
      '/productos': { target: apiProxyTarget, changeOrigin: true },
      '/notificaciones': { target: apiProxyTarget, changeOrigin: true },
      '/health': { target: apiProxyTarget, changeOrigin: true },
    }
  }
})