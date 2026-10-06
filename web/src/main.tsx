import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import '@fontsource/jomolhari/tibetan-400.css'
import './styles.css'
import { App } from './App'
import { SettingsProvider } from './settings'

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <SettingsProvider>
      <App />
    </SettingsProvider>
  </StrictMode>,
)
