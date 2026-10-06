import { useEffect, useState } from 'react'
import { curriculum, type Item } from '../content'
import { load, save } from '../storage'
import { AudioButton, Tib, TopBar } from '../ui'

type Status = 'candidate' | 'approved' | 'rejected'
const KEY = 'lt.v1.audioReview'

/** Curation aid: listen to every clip (candidates included) and mark it. The result is copied as
 *  "item status" lines for `tools/audio/curate.py status`, which updates content/audio.toml. */
export function AudioReview() {
  const clips = curriculum.items.filter((it) => it.audio)
  const [marks, setMarks] = useState<Record<string, Status>>(() => load(KEY, {}))
  const [copied, setCopied] = useState('')
  useEffect(() => save(KEY, marks), [marks])

  const statusOf = (it: Item): Status => marks[it.id] ?? it.audio!.status
  const changed = clips.filter((it) => marks[it.id] && marks[it.id] !== it.audio!.status)
  const text = changed.map((it) => `${it.id} ${marks[it.id]}`).join('\n')
  const copy = async () => {
    try {
      await navigator.clipboard.writeText(text)
      setCopied('Kopiert.')
    } catch {
      setCopied(text) // clipboard unavailable (e.g. http on a phone): show for manual copy
    }
  }

  return (
    <div className="screen">
      <TopBar title="Audio prüfen" />
      <main className="review">
        <p className="note">
          Alle Clips inkl. KI-Kandidaten. Im Lernen werden nur freigegebene (✓) Clips verwendet. Änderungen
          kopieren und mit <code>tools/audio/curate.py status</code> übernehmen.
        </p>
        <ul>
          {clips.map((it) => {
            const st = statusOf(it)
            return (
              <li key={it.id} className={`review-row ${st}`}>
                <AudioButton it={it} any />
                <Tib className="review-glyph">{it.tibetan}</Tib>
                <span className="review-meta">
                  <span className="wylie">{it.wylie}</span>
                  <small>{it.audio!.source}</small>
                </span>
                <button className="mark ok" aria-pressed={st === 'approved'} onClick={() => setMarks({ ...marks, [it.id]: 'approved' })} aria-label="freigeben">
                  ✓
                </button>
                <button className="mark no" aria-pressed={st === 'rejected'} onClick={() => setMarks({ ...marks, [it.id]: 'rejected' })} aria-label="verwerfen">
                  ✗
                </button>
              </li>
            )
          })}
        </ul>
        <div className="review-foot">
          <button className="btn primary" disabled={!changed.length} onClick={copy}>
            {changed.length} Änderungen kopieren
          </button>
          {copied && <pre className="copied">{copied}</pre>}
        </div>
      </main>
    </div>
  )
}
