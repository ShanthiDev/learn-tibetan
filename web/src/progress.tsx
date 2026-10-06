import { createContext, useContext, useEffect, useState, type ReactNode } from 'react'
import { emptyProgress, type Progress } from './engine/progress'
import { load, save } from './storage'

const KEY = 'lt.v1.progress'
type Ctx = { progress: Progress; setProgress: (p: Progress) => void; reset: () => void }
const ProgressContext = createContext<Ctx>({ progress: emptyProgress(), setProgress: () => {}, reset: () => {} })

export function ProgressProvider({ children }: { children: ReactNode }) {
  const [progress, setProgress] = useState<Progress>(() => {
    const p = load(KEY, emptyProgress())
    return p.v === 1 ? p : emptyProgress()
  })
  useEffect(() => save(KEY, progress), [progress])
  return (
    <ProgressContext.Provider value={{ progress, setProgress, reset: () => setProgress(emptyProgress()) }}>
      {children}
    </ProgressContext.Provider>
  )
}

export const useProgress = () => useContext(ProgressContext)
