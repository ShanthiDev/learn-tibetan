import type { ReactNode } from 'react'
import { go } from './router'

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
