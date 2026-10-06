import { hasAudio, type Curriculum, type Item, type Lesson, type QuizMode } from '../content'
import { CONFIG } from './config'
import { keyOf, statOf, type Progress } from './progress'
import type { Scope } from './question'
import type { Rng } from './rng'

export type Entry = { key: string; itemId: string; mode: QuizMode; scope: Scope; isNew: boolean }
export type SessionKind = { kind: 'learn'; lessonId: string } | { kind: 'practice' } | { kind: 'review' }

const scopeOf = (l: Lesson): Scope => (l.chapter === 4 || l.id === 'a3' ? 'syllables' : 'letters')

function entries(l: Lesson, isNew: boolean, item: (id: string) => Item): Entry[] {
  return l.newItemIds.flatMap((itemId) =>
    l.modes
      .filter((mode) => mode !== 'audio-tib' || hasAudio(item(itemId)))
      .map((mode) => ({ key: keyOf(itemId, mode), itemId, mode, scope: scopeOf(l), isNew })),
  )
}

function dedupe(es: Entry[]): Entry[] {
  const seen = new Map<string, Entry>()
  for (const e of es) if (!seen.has(e.key) || e.isNew) seen.set(e.key, e)
  return [...seen.values()]
}

const isDifficult = (p: Progress, key: string) => {
  const s = statOf(p, key)
  return s.mistakes.some((m) => p.counter - m < 200) || (s.seen >= 2 && s.correct / s.seen < 0.7)
}

/** Question pool of a session: current lesson + cumulative review of everything unlocked before it. */
export function buildPool(
  session: SessionKind,
  p: Progress,
  c: Curriculum,
  unlocked: number,
  item: (id: string) => Item,
): Entry[] {
  const open = c.lessons.slice(0, unlocked)
  if (session.kind === 'learn') {
    const idx = c.lessons.findIndex((l) => l.id === session.lessonId)
    const earlier = c.lessons.slice(0, Math.min(idx, unlocked)).flatMap((l) => entries(l, false, item))
    return dedupe([...earlier, ...entries(c.lessons[idx], true, item)])
  }
  const all = dedupe(open.flatMap((l) => entries(l, false, item))).filter((e) => statOf(p, e.key).seen > 0)
  return session.kind === 'practice' ? all : all.filter((e) => isDifficult(p, e.key))
}

/** Next question: due mistakes first, otherwise weighted by weakness (not uniform). */
export function pickNext(pool: Entry[], p: Progress, rng: Rng): Entry | null {
  if (!pool.length) return null
  const byKey = new Map(pool.map((e) => [e.key, e]))
  const due = p.retry.filter((r) => r.due <= p.counter + 1 && byKey.has(r.key)).sort((a, b) => a.due - b.due)[0]
  if (due && p.recent[p.recent.length - 1] !== due.key) return byKey.get(due.key)!
  const fresh = pool.length > CONFIG.recentExclude + 1 ? pool.filter((e) => !p.recent.includes(e.key)) : pool
  const weights = fresh.map((e) => (CONFIG.maxBox + 1 - statOf(p, e.key).box) ** 2 * (e.isNew ? CONFIG.newWeight : 1))
  let r = rng() * weights.reduce((a, b) => a + b, 0)
  for (let i = 0; i < fresh.length; i++) if ((r -= weights[i]) < 0) return fresh[i]
  return fresh[fresh.length - 1]
}

export const difficultCount = (p: Progress, c: Curriculum, unlocked: number, item: (id: string) => Item) =>
  buildPool({ kind: 'review' }, p, c, unlocked, item).length
