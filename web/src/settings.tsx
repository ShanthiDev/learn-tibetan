import { createContext, useContext, useEffect, useState, type ReactNode } from 'react'
import { load, save } from './storage'

export type Settings = {
  showDevanagari: boolean
  showTz: boolean
  autoplayAudio: boolean
  sfx: boolean
  volume: number
  unlockAll: boolean
}

const KEY = 'lt.v1.settings'
const DEFAULTS: Settings = { showDevanagari: false, showTz: true, autoplayAudio: true, sfx: true, volume: 0.8, unlockAll: false }

type Ctx = [Settings, (patch: Partial<Settings>) => void]
const SettingsContext = createContext<Ctx>([DEFAULTS, () => {}])

export function SettingsProvider({ children }: { children: ReactNode }) {
  const [settings, setSettings] = useState<Settings>(() => load(KEY, DEFAULTS))
  useEffect(() => save(KEY, settings), [settings])
  const update = (patch: Partial<Settings>) => setSettings((s) => ({ ...s, ...patch }))
  return <SettingsContext.Provider value={[settings, update]}>{children}</SettingsContext.Provider>
}

export const useSettings = () => useContext(SettingsContext)
