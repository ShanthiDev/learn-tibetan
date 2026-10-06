import { useState, type MouseEvent, type ReactNode } from 'react'
import { playFile, playItem } from './audio'
import { hasAudio, phonologyOf, vowelOf, type Item } from './content'
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

export function AudioButton({ it, big = false, any = false, file }: { it?: Item; big?: boolean; any?: boolean; file?: string }) {
  const [settings] = useSettings()
  if (!file && !(it && (any ? it.audio : hasAudio(it)))) return null
  const play = (e: MouseEvent) => {
    e.stopPropagation()
    if (file) playFile(file, settings.volume)
    else playItem(it!, settings.volume, settings.variant)
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

/** Small ⓘ toggle: extra knowledge stays hidden until asked for. */
export function Info({ children, label = 'Mehr Info' }: { children: ReactNode; label?: string }) {
  const [open, setOpen] = useState(false)
  return (
    <>
      <button className={`info-btn ${open ? 'open' : ''}`} aria-expanded={open} aria-label={label} onClick={(e) => { e.stopPropagation(); setOpen(!open) }}>
        i
      </button>
      {open && <div className="info-box">{children}</div>}
    </>
  )
}

/** One line about how a letter (or the vowel of a vowel form) sounds. */
export function SoundFacts({ it, hint = true }: { it: Item; hint?: boolean }) {
  const ph = phonologyOf(it)
  const v = vowelOf(it)
  return (
    <span className="sound-facts">
      {ph && (
        <span>
          {[ph.aspiration, ph.tone === 'hoch' ? 'hoher Ton' : 'tiefer Ton'].filter(Boolean).join(' · ')}
          {hint && it.kind === 'letter' && <small> – <Rich text={ph.hintDe} /></small>}
        </span>
      )}
      {it.kind === 'vowel-form' && (
        <small>
          Vokal {v.id}: {v.soundDe}
        </small>
      )}
    </span>
  )
}

/** Plain text with Tibetan runs enlarged (Jomolhari is small on the em; Latin text stays as is). */
export function Rich({ text }: { text: string }) {
  return (
    <>
      {text.split(/([\u0F00-\u0FFF]+)/).map((part, i) =>
        i % 2 ? (
          <span key={i} className="tib tib-inline" lang="bo">
            {part}
          </span>
        ) : (
          part
        ),
      )}
    </>
  )
}
