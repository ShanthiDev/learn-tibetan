import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import { VitePWA } from 'vite-plugin-pwa'

export default defineConfig({
  base: './',
  plugins: [
    react(),
    VitePWA({
      registerType: 'autoUpdate',
      includeAssets: ['icon-192.png', 'icon-512.png', 'favicon.png'],
      manifest: {
        name: 'Tibetisch lesen',
        short_name: 'Tibetisch',
        description: 'Tibetische Schrift (Uchen) lesen lernen',
        lang: 'de',
        start_url: './',
        display: 'standalone',
        orientation: 'portrait',
        theme_color: '#6F2634',
        background_color: '#F4EBDD',
        icons: [
          { src: 'icon-192.png', sizes: '192x192', type: 'image/png' },
          { src: 'icon-512.png', sizes: '512x512', type: 'image/png' },
          { src: 'icon-512.png', sizes: '512x512', type: 'image/png', purpose: 'maskable' },
        ],
      },
      workbox: {
        globPatterns: ['**/*.{js,css,html,png,svg,woff2,mp3}'],
        ignoreURLParametersMatching: [/^v$/], // audio cache-busting hash (?v=…) must still hit the precache
      },
    }),
  ],
})
