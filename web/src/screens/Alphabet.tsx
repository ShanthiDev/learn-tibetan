import { useEffect, useState } from 'react'
import { curriculum, groupsById, item, phonologyOf, vowelOf, type Item } from '../content'
import { useSettings } from '../settings'
import { AudioButton, Rich, Tib, TopBar } from '../ui'

export function Alphabet() {
  const [settings] = useSettings()
  const [detail, setDetail] = useState<Item | null>(null)
  const [topics, setTopics] = useState(false)
  const ka = curriculum.items.filter((it) => it.baseId === 'l-ka')

  return (
    <div className="screen">
      <TopBar
        title="Alphabet"
        right={
          <button className="icon-btn" onClick={() => setTopics(true)} aria-label="Hintergrundwissen">
            <span className="info-btn on-dark">i</span>
          </button>
        }
      />
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

        <p className="note">
          <Rich text={curriculum.alphabetNoteDe} />{' '}
          <button className="link" onClick={() => setTopics(true)}>
            Mehr zu Behauchung, Ton &amp; Co.
          </button>
        </p>
      </main>
      {detail && <Detail it={detail} onClose={() => setDetail(null)} />}
      {topics && <Topics onClose={() => setTopics(false)} />}
    </div>
  )
}

function Detail({ it, onClose }: { it: Item; onClose: () => void }) {
  const [settings] = useSettings()
  const g = groupsById.get(it.groupId)!
  const vowel = vowelOf(it)
  const ph = phonologyOf(it)
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
          {ph && it.kind === 'letter' && (
            <>
              <dt>Aussprache</dt>
              <dd>
                {[ph.aspiration, ph.tone === 'hoch' ? 'hoher Ton' : 'tiefer Ton'].filter(Boolean).join(' · ')}
                <small className="block">
                  <Rich text={ph.hintDe} />
                </small>
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
                {it.vowel} <small>· {vowel.soundDe}</small>
                {vowel.nameSpoken && (
                  <small className="block">
                    Zeichenname {vowel.nameDe} (gesprochen „{vowel.nameSpoken}“)
                    {vowel.nameAudio && <AudioButton file={vowel.nameAudio} />}
                  </small>
                )}
                {vowel.example && (
                  <small className="block">
                    Beispiel: <Tib>{vowel.example.tibetan}</Tib> {vowel.example.wylie} „{vowel.example.meaningDe}“
                    <AudioButton file={vowel.example.audio} />
                  </small>
                )}
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

function Topics({ onClose }: { onClose: () => void }) {
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => e.key === 'Escape' && onClose()
    addEventListener('keydown', onKey)
    return () => removeEventListener('keydown', onKey)
  }, [onClose])
  return (
    <div className="sheet-backdrop" onClick={onClose}>
      <div className="sheet topics" role="dialog" aria-modal="true" aria-label="Hintergrundwissen" onClick={(e) => e.stopPropagation()}>
        <h2>Hintergrundwissen</h2>
        {curriculum.topics.map((t, i) => (
          <details key={t.id} open={i === 0}>
            <summary>
              <Rich text={t.titleDe} />
            </summary>
            {t.textDe.split('\n\n').map((para, j) => (
              <p key={j}>
                <Rich text={para} />
              </p>
            ))}
          </details>
        ))}
        <button className="btn" onClick={onClose} autoFocus>
          Schließen
        </button>
      </div>
    </div>
  )
}
