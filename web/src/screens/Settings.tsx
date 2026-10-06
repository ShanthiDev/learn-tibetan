import type { ReactNode } from 'react'
import { go } from '../router'
import { useSettings } from '../settings'
import { TopBar } from '../ui'

export function SettingsScreen({ onReset }: { onReset: () => void }) {
  const [s, update] = useSettings()
  return (
    <div className="screen">
      <TopBar title="Einstellungen" />
      <main className="settings">
        <Toggle label="Devanagari-Parallelen zeigen" checked={s.showDevanagari} onChange={(v) => update({ showDevanagari: v })} />
        <Toggle label="TZ-Aussprache in Referenzansichten" checked={s.showTz} onChange={(v) => update({ showTz: v })} />
        <Toggle label="Audio automatisch abspielen" checked={s.autoplayAudio} onChange={(v) => update({ autoplayAudio: v })} />
        <Toggle label="Feedback-Töne" checked={s.sfx} onChange={(v) => update({ sfx: v })} />
        <label className="row">
          <span>Lautstärke</span>
          <input type="range" min={0} max={1} step={0.1} value={s.volume} onChange={(e) => update({ volume: +e.target.value })} />
        </label>
        <Toggle label="Alle Lektionen freischalten" checked={s.unlockAll} onChange={(v) => update({ unlockAll: v })} />
        <Row>
          <button className="btn" onClick={() => go('audio-review')}>
            Audio-Clips prüfen
          </button>
        </Row>
        <Row>
          <button
            className="btn danger"
            onClick={() => confirm('Gesamten Lernfortschritt löschen?') && onReset()}
          >
            Fortschritt zurücksetzen
          </button>
        </Row>
      </main>
    </div>
  )
}

const Row = ({ children }: { children: ReactNode }) => <div className="row">{children}</div>

function Toggle({ label, checked, onChange }: { label: string; checked: boolean; onChange: (v: boolean) => void }) {
  return (
    <label className="row">
      <span>{label}</span>
      <input type="checkbox" role="switch" checked={checked} onChange={(e) => onChange(e.target.checked)} />
    </label>
  )
}
