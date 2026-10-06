import { useEffect, useState } from 'react'
import { curriculum, groupsById, item, type Item } from '../content'
import { useSettings } from '../settings'
import { AudioButton, Tib, TopBar } from '../ui'

export function Alphabet() {
  const [settings] = useSettings()
  const [detail, setDetail] = useState<Item | null>(null)
  const ka = curriculum.items.filter((it) => it.baseId === 'l-ka')

  return (
    <div className="screen">
      <TopBar title="Alphabet" />
      <main className="alphabet">
        {curriculum.groups.map((g) => (
          <section key={g.id} aria-label={g.labelDe}>
            <h2 className="group-head">
              <span>{g.labelDe}</span>
              {g.linguistic && <small>{g.linguistic}</small>}
            </h2>
            <div className="grid4">
              {g.itemIds.map((id) => {
                const it = item(id)
                return (
                  <button key={id} className="cell" onClick={() => setDetail(it)}>
                    <Tib tsheg className="cell-glyph">{it.tibetan}</Tib>
                    <span className="cell-band">
                      <span className="wylie">{it.wylie}</span>
                      {settings.showTz && <span className="cell-sub">{it.tz}</span>}
                      {settings.showDevanagari && <span className="cell-sub deva">{it.devanagari ?? '–'}</span>}
                    </span>
                  </button>
                )
              })}
            </div>
          </section>
        ))}

        <section aria-label="Vokale">
          <h2 className="group-head">
            <span>Vokalzeichen</span>
            <small>auf ཀ</small>
          </h2>
          <div className="grid5">
            {ka.map((it) => (
              <button key={it.id} className="cell" onClick={() => setDetail(it)}>
                <Tib tsheg className="cell-glyph small">{it.tibetan}</Tib>
                <span className="cell-band">
                  <span className="wylie">{it.wylie}</span>
                  {settings.showTz && <span className="cell-sub">{it.tz}</span>}
                </span>
              </button>
            ))}
          </div>
        </section>

        <p className="note">{curriculum.alphabetNoteDe}</p>
      </main>
      {detail && <Detail it={detail} onClose={() => setDetail(null)} />}
    </div>
  )
}

function Detail({ it, onClose }: { it: Item; onClose: () => void }) {
  const [settings] = useSettings()
  const g = groupsById.get(it.groupId)!
  const vowel = curriculum.vowels.find((v) => v.id === it.vowel)!
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => e.key === 'Escape' && onClose()
    addEventListener('keydown', onKey)
    return () => removeEventListener('keydown', onKey)
  }, [onClose])

  return (
    <div className="sheet-backdrop" onClick={onClose}>
      <div className="sheet" role="dialog" aria-modal="true" aria-label={it.wylie} onClick={(e) => e.stopPropagation()}>
        <div className="sheet-head">
          <Tib className="sheet-glyph">{it.tibetan}</Tib>
          <AudioButton it={it} big />
        </div>
        <dl className="facts">
          <dt>Wylie</dt>
          <dd className="wylie">{it.wylie}</dd>
          <dt>TZ-Aussprache</dt>
          <dd>{it.tz}</dd>
          {(settings.showDevanagari || it.kind === 'letter') && (
            <>
              <dt>Devanagari</dt>
              <dd>
                {it.devanagari && <span className="deva">{it.devanagari}</span>}
                {it.devanagariNote && <small> {it.devanagariNote}</small>}
                {!it.devanagari && !it.devanagariNote && '–'}
              </dd>
            </>
          )}
          <dt>Reihe</dt>
          <dd>
            {g.labelDe}
            {g.linguistic && <small> · {g.linguistic}</small>}
          </dd>
          {it.kind === 'vowel-form' && (
            <>
              <dt>Vokal</dt>
              <dd>
                {it.vowel} <small>({vowel.nameDe})</small>
              </dd>
            </>
          )}
        </dl>
        <button className="btn" onClick={onClose} autoFocus>
          Schließen
        </button>
      </div>
    </div>
  )
}
