import { useCallback, useEffect, useRef, useState } from 'react'
import { playItem } from '../audio'
import { curriculum, hasAudio, item, type Item, type Lesson } from '../content'
import { CONFIG } from '../engine/config'
import { applyAnswer, lessonMastered, lessonScore, lessonStarted, type Progress } from '../engine/progress'
import { makeQuestion, type Question } from '../engine/question'
import { buildPool, pickNext, type SessionKind } from '../engine/select'
import { pathState } from '../lessons'
import { sfx } from '../sfx'
import { useProgress } from '../progress'
import { go } from '../router'
import { useSettings } from '../settings'
import { AudioButton, Info, SoundFacts, Tib } from '../ui'

type Phase = 'intro' | 'ask' | 'feedback' | 'done' | 'empty'
const rng = Math.random

function nextQuestion(session: SessionKind, p: Progress, unlocked: number): Question | null {
  const pool = buildPool(session, p, curriculum, unlocked, item)
  const known = new Set(Object.keys(p.stats).map((k) => k.split('|')[0]))
  for (let tries = 0; tries < 12; tries++) {
    const e = pickNext(pool, p, rng)
    if (!e) return null
    const q = makeQuestion(item(e.itemId), e.mode, e.scope, curriculum, known, rng)
    if (q) return q
  }
  return null
}

export function Quiz({ session }: { session: SessionKind }) {
  const { progress, setProgress } = useProgress()
  const [settings] = useSettings()
  const lesson = session.kind === 'learn' ? curriculum.lessons.find((l) => l.id === session.lessonId) : undefined
  const unlocked = pathState(progress, settings.unlockAll).unlocked

  const [phase, setPhase] = useState<Phase>(() =>
    lesson?.introItemIds && !lessonStarted(progress, lesson) ? 'intro' : 'ask',
  )
  const [q, setQ] = useState<Question | null>(null)
  const [selected, setSelected] = useState<number | null>(null) // step 1: tapped, not yet checked
  const [chosen, setChosen] = useState<number | null>(null) // step 2: confirmed answer
  const [tally, setTally] = useState({ right: 0, total: 0 })
  const timer = useRef<number | undefined>(undefined)
  const pending = useRef<Progress>(progress)
  const mastered = useRef(false)

  const advance = useCallback(
    (p: Progress) => {
      clearTimeout(timer.current)
      const next = nextQuestion(session, p, unlocked)
      setQ(next)
      setSelected(null)
      setChosen(null)
      setPhase(next ? 'ask' : 'empty')
    },
    [session, unlocked],
  )

  // first question (after the intro card, if any)
  useEffect(() => {
    if (phase === 'ask' && !q) advance(progress)
  }, [phase, q, advance, progress])
  useEffect(() => () => clearTimeout(timer.current), [])
  useEffect(() => {
    if (q?.mode === 'audio-tib' && settings.autoplayAudio) playItem(q.target, settings.volume, settings.variant)
  }, [q]) // only when a new question appears

  const answer = (i: number) => {
    if (phase !== 'ask' || !q) return
    const correct = i === q.correctIndex
    const key = `${q.target.id}|${q.mode}`
    const p = applyAnswer(progress, key, correct, rng)
    const justMastered = !!lesson && !lessonMastered(progress, lesson, item) && lessonMastered(p, lesson, item)
    pending.current = p
    mastered.current = justMastered
    setProgress(p)
    setChosen(i)
    setPhase('feedback')
    setTally((t) => ({ right: t.right + (correct ? 1 : 0), total: t.total + 1 }))
    navigator.vibrate?.(correct ? 12 : [30, 40, 30])
    if (settings.sfx) sfx(correct ? 'correct' : 'wrong', settings.volume)
    // the options were already heard while choosing; after a mistake, play the right one once more
    if (!correct && q.mode !== 'audio-tib' && settings.autoplayAudio && hasAudio(q.target))
      window.setTimeout(() => playItem(q.target, settings.volume, settings.variant), settings.sfx ? 380 : 0)
    // correct: move on by itself; wrong: stop until the learner presses "Weiter"
    if (correct)
      timer.current = window.setTimeout(() => (justMastered ? setPhase('done') : advance(p)), CONFIG.correctDelayMs)
  }

  /** Step 1: select an option and hear it (not in listening questions: that would give it away). */
  const select = (i: number) => {
    if (phase !== 'ask' || !q) return
    setSelected(i)
    const o = q.options[i]
    if (q.mode !== 'audio-tib' && hasAudio(o)) playItem(o, settings.volume, settings.variant)
  }

  const proceed = () => {
    if (phase !== 'feedback') return
    clearTimeout(timer.current)
    if (mastered.current) setPhase('done')
    else advance(pending.current)
  }

  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (e.key === 'Escape') return go('home')
      if (e.key === ' ' && phase === 'ask' && q?.mode === 'audio-tib') {
        e.preventDefault()
        playItem(q.target, settings.volume, settings.variant)
      } else if (phase === 'ask' && /^[1-4]$/.test(e.key)) select(+e.key - 1)
      else if (phase === 'ask' && e.key === 'Enter' && selected !== null) {
        e.preventDefault()
        answer(selected)
      } else if (phase === 'feedback' && (e.key === 'Enter' || e.key === ' ')) {
        e.preventDefault()
        proceed()
      }
    }
    addEventListener('keydown', onKey)
    return () => removeEventListener('keydown', onKey)
  })

  const score = lesson ? lessonScore(progress, lesson, item) : null
  const wrong = phase === 'feedback' && q !== null && chosen !== null && chosen !== q.correctIndex

  return (
    <div className="screen quiz">
      <header className="quiz-bar">
        <button className="icon-btn" onClick={() => go('home')} aria-label="Beenden">
          ×
        </button>
        <span className="meter wide" aria-label="Fortschritt">
          <span style={{ width: `${(score ?? 0) * 100}%` }} />
        </span>
        <span className="tally" aria-label="richtig von gesamt">
          {tally.right}/{tally.total}
        </span>
      </header>

      {phase === 'intro' && lesson && <Intro lesson={lesson} onStart={() => setPhase('ask')} />}
      {phase === 'done' && lesson && <Done lesson={lesson} />}
      {phase === 'empty' && (
        <div className="center-card">
          <p>{session.kind === 'review' ? 'Gerade nichts Schwieriges. Sehr gut!' : 'Noch nichts zu üben.'}</p>
          <button className="btn primary" onClick={() => go('home')}>
            Zur Übersicht
          </button>
        </div>
      )}
      {(phase === 'ask' || phase === 'feedback') && q && (
        <Ask q={q} selected={selected} chosen={chosen} onSelect={select} />
      )}
      {wrong && <Oops q={q!} chosen={q!.options[chosen!]} onNext={proceed} />}
      {(phase === 'ask' || phase === 'feedback') && q && !wrong && (
        <div className="confirm-bar">
          <button
            className={`btn confirm ${phase === 'feedback' ? 'ok' : ''}`}
            disabled={selected === null && phase === 'ask'}
            onClick={() => selected !== null && answer(selected)}
          >
            {phase === 'feedback' ? '✓ Richtig' : 'Prüfen'}
          </button>
        </div>
      )}
    </div>
  )
}

function Ask({ q, selected, chosen, onSelect }: { q: Question; selected: number | null; chosen: number | null; onSelect: (i: number) => void }) {
  const tibAnswers = q.mode !== 'tib-wylie'
  return (
    <>
      <div className="prompt" aria-live="polite">
        {q.mode === 'tib-wylie' && <Tib className="prompt-glyph">{q.target.tibetan}</Tib>}
        {q.mode === 'wylie-tib' && <span className="prompt-wylie wylie">{q.target.wylie}</span>}
        {q.mode === 'audio-tib' && <AudioButton it={q.target} big />}
      </div>
      <div className={`options ${tibAnswers ? 'tib-options' : ''}`}>
        {q.options.map((o: Item, i) => {
          const state =
            chosen === null
              ? i === selected
                ? 'selected'
                : ''
              : i === q.correctIndex
                ? 'correct'
                : i === chosen
                  ? 'wrong'
                  : 'dim'
          return (
            <button
              key={o.id}
              className={`opt ${state}`}
              onClick={(e) => {
                e.stopPropagation()
                onSelect(i)
              }}
              aria-label={tibAnswers ? `Antwort ${i + 1}` : o.wylie}
              aria-pressed={i === selected}
              aria-disabled={chosen !== null}
            >
              {tibAnswers ? <Tib>{o.tibetan}</Tib> : <span className="wylie">{o.wylie}</span>}
              <kbd aria-hidden>{i + 1}</kbd>
            </button>
          )
        })}
      </div>
    </>
  )
}

function Oops({ q, chosen, onNext }: { q: Question; chosen: Item; onNext: () => void }) {
  const [settings] = useSettings()
  const t = q.target
  const pair = (it: Item) => (
    <>
      <Tib>{it.tibetan}</Tib> <span className="eq">=</span> <span className="wylie">{it.wylie}</span>
    </>
  )
  return (
    <section className="oops" role="alert">
      <div className="oops-head">
        <span className="oops-x" aria-hidden>
          ✕
        </span>
        <h2>Oops, nicht ganz.</h2>
        <AudioButton it={t} />
      </div>
      <p className="oops-right">
        Richtig: {pair(t)}
        {settings.showTz && t.tz !== t.wylie && <small> · gesprochen „{t.tz}“</small>}
      </p>
      <p className="oops-chosen">Deine Wahl: {pair(chosen)}</p>
      <div className="oops-info">
        <Info label="Unterschied erklären">
          {[t, chosen].map((it) => (
            <p key={it.id}>
              <Tib>{it.tibetan}</Tib> <SoundFacts it={it} />
            </p>
          ))}
        </Info>
      </div>
      <button className="btn oops-next" onClick={onNext} autoFocus>
        Weiter
      </button>
    </section>
  )
}

function Intro({ lesson, onStart }: { lesson: Lesson; onStart: () => void }) {
  const [settings] = useSettings()
  const items = (lesson.introItemIds ?? []).map(item)
  const vowels = lesson.chapter === 4
  return (
    <div className="intro">
      <p className="eyebrow">{vowels ? 'Neu: Vokalzeichen' : 'Neue Reihe'}</p>
      <h2>{vowels ? 'Vokale auf ཀ' : curriculum.groups.find((g) => g.id === items[0].groupId)?.labelDe}</h2>
      <div className={vowels ? 'grid5' : 'grid4'}>
        {items.map((it) => (
          <div key={it.id} className="cell">
            <Tib tsheg className={`cell-glyph ${vowels ? 'small' : ''}`}>{it.tibetan}</Tib>
            <span className="cell-band">
              <span className="wylie">{it.wylie}</span>
              {settings.showTz && <span className="cell-sub">{it.tz}</span>}
              {settings.showDevanagari && it.devanagari && <span className="cell-sub deva">{it.devanagari}</span>}
              {vowels && <span className="cell-sub">{curriculum.vowels.find((v) => v.id === it.vowel)?.nameDe}</span>}
              <AudioButton it={it} />
            </span>
          </div>
        ))}
      </div>
      <div className="intro-info">
        <Info label="Aussprache der neuen Zeichen">
          {vowels
            ? curriculum.vowels
                .filter((v) => v.sign)
                .map((v) => (
                  <p key={v.id}>
                    <Tib>{`ཀ${v.sign}`}</Tib> <b>{v.id}</b> {v.soundDe}
                    {v.nameSpoken && <small> · Name: {v.nameDe} („{v.nameSpoken}“)</small>}
                    {v.nameAudio && <AudioButton file={v.nameAudio} />}
                    {v.example && (
                      <small className="block">
                        z. B. <Tib>{v.example.tibetan}</Tib> {v.example.wylie} „{v.example.meaningDe}“
                        <AudioButton file={v.example.audio} />
                      </small>
                    )}
                  </p>
                ))
            : items.map((it) => (
                <p key={it.id}>
                  <Tib>{it.tibetan}</Tib> <b>{it.wylie}</b> <SoundFacts it={it} />
                </p>
              ))}
        </Info>
      </div>
      <p className="note">
        Abgefragt wird die Wylie-Umschrift (Buchstaben), nicht die Aussprache.
        {settings.showTz && ' Die zweite Zeile zeigt die TZ-Aussprache als Lesehilfe.'}
      </p>
      <button className="btn primary big" onClick={onStart} autoFocus>
        Los geht’s
      </button>
    </div>
  )
}

function Done({ lesson }: { lesson: Lesson }) {
  const { progress } = useProgress()
  const [settings] = useSettings()
  const { current } = pathState(progress, settings.unlockAll)
  return (
    <div className="center-card">
      <p className="big-check" aria-hidden>
        ✓
      </p>
      <h2>Gemeistert</h2>
      <p>{lesson.titleDe}</p>
      {current && (
        <button className="btn primary big" onClick={() => go('learn', current.lesson.id)} autoFocus>
          Weiter: {current.lesson.titleDe}
        </button>
      )}
      <button className="btn" onClick={() => go('home')}>
        Zur Übersicht
      </button>
    </div>
  )
}
