import type { MouseEvent, ReactNode } from 'react'
import { playItem } from './audio'
import { hasAudio, type Item } from './content'
import { go } from './router'
import { useSettings } from './settings'

export function TopBar({ title, right, back = true }: { title: ReactNode; right?: ReactNode; back?: boolean }) {
  return (
    <header className="topbar">
      {back ? (
        <button className="icon-btn" onClick={() => go('home')} aria-label="Zurück">
          ‹
        </button>
      ) : (
        <span className="icon-btn" aria-hidden />
      )}
      <h1>{title}</h1>
      {right ?? <span className="icon-btn" aria-hidden />}
    </header>
  )
}

/** Tibetan text in the app font; `tsheg` appends the syllable dot as in traditional charts. */
export function Tib({ children, tsheg, className = '' }: { children: string; tsheg?: boolean; className?: string }) {
  return (
    <span className={`tib ${className}`} lang="bo">
      {children}
      {tsheg && <span className="tsheg">་</span>}
    </span>
  )
}

export function AudioButton({ it, big = false, any = false }: { it: Item; big?: boolean; any?: boolean }) {
  const [settings] = useSettings()
  if (!(any ? it.audio : hasAudio(it))) return null
  const play = (e: MouseEvent) => {
    e.stopPropagation()
    playItem(it, settings.volume)
  }
  return (
    <button className={`audio-btn ${big ? 'big' : ''}`} onClick={play} aria-label="Anhören">
      <svg viewBox="0 0 24 24" aria-hidden>
        <path d="M4 9v6h4l5 4V5L8 9H4z" fill="currentColor" />
        <path d="M16 8.5a5 5 0 0 1 0 7M18.5 6a8.5 8.5 0 0 1 0 12" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
      </svg>
    </button>
  )
}
