import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import { VitePWA } from 'vite-plugin-pwa'

export default defineConfig({
  plugins: [react(), VitePWA({
    registerType: 'autoUpdate',
    includeAssets: ['favicon.ico', 'icons/*'],
    manifest: {
      name: 'BrickFarm',
      short_name: 'BrickFarm',
      start_url: '/',
      display: 'standalone',
      background_color: '#ffffff',
      theme_color: '#184914'
    },
    workbox: {
      runtimeCaching: [
        {
          urlPattern: /\/api\//,
          handler: 'NetworkFirst',
          options: { cacheName: 'api-cache' }
        },
        {
          urlPattern: /\.(?:png|jpg|jpeg|svg|gif|webp)$/,
          handler: 'CacheFirst',
          options: { cacheName: 'image-cache' }
        }
      ]
    }
  })],
  server: {
    host: true,
    port: 5173
  }
})
