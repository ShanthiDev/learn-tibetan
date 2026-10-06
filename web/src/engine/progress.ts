import { hasAudio, type Item, type Lesson, type QuizMode } from '../content'
import { CONFIG } from './config'
import type { Rng } from './rng'

export type Stat = { seen: number; correct: number; box: number; last: number; mistakes: number[] }
export type Progress = {
  v: 1
  counter: number // questions answered overall; used as the clock
  stats: Record<string, Stat>
  retry: { key: string; due: number }[]
  recent: string[]
}

export const keyOf = (itemId: string, mode: QuizMode) => `${itemId}|${mode}`
export const emptyProgress = (): Progress => ({ v: 1, counter: 0, stats: {}, retry: [], recent: [] })
const emptyStat = (): Stat => ({ seen: 0, correct: 0, box: 0, last: -1, mistakes: [] })
export const statOf = (p: Progress, key: string): Stat => p.stats[key] ?? emptyStat()

export function applyAnswer(p: Progress, key: string, correct: boolean, rng: Rng): Progress {
  const counter = p.counter + 1
  const s = statOf(p, key)
  const stat: Stat = {
    seen: s.seen + 1,
    correct: s.correct + (correct ? 1 : 0),
    box: correct ? Math.min(CONFIG.maxBox, s.box + 1) : Math.max(0, s.box - CONFIG.wrongPenalty),
    last: counter,
    mistakes: correct ? s.mistakes : [...s.mistakes, counter].slice(-CONFIG.mistakeMemory),
  }
  const [lo, hi] = CONFIG.retryAfter
  const retry = p.retry.filter((r) => r.key !== key)
  if (!correct) retry.push({ key, due: counter + lo + Math.floor(rng() * (hi - lo + 1)) })
  return {
    ...p,
    counter,
    stats: { ...p.stats, [key]: stat },
    retry,
    recent: [...p.recent, key].slice(-CONFIG.recentExclude),
  }
}

/** Items of a lesson that can actually be asked (audio lessons need a clip). */
export const playableItems = (lesson: Lesson, items: (id: string) => Item) =>
  lesson.newItemIds.filter((id) => !lesson.modes.includes('audio-tib') || hasAudio(items(id)))

/** 0..1: how close the lesson is to mastery. Each item/mode counts up to the lesson's mastery box;
 *  1 is reached when the required share of the lesson's item/modes is fully there. */
export function lessonScore(p: Progress, lesson: Lesson, items: (id: string) => Item): number {
  const ids = playableItems(lesson, items)
  if (!ids.length) return 0
  const { box, share } = lesson.mastery ?? { box: CONFIG.masteredBox, share: 1 }
  let sum = 0
  for (const id of ids) for (const m of lesson.modes) sum += Math.min(box, statOf(p, keyOf(id, m)).box) / box
  return Math.min(1, sum / (ids.length * lesson.modes.length * share))
}

export const lessonMastered = (p: Progress, lesson: Lesson, items: (id: string) => Item) =>
  playableItems(lesson, items).length > 0 && lessonScore(p, lesson, items) >= 1

export const lessonStarted = (p: Progress, lesson: Lesson) =>
  lesson.newItemIds.some((id) => lesson.modes.some((m) => statOf(p, keyOf(id, m)).seen > 0))

/** Linear path: a lesson is unlocked when the previous playable lesson is mastered. */
export function unlockedCount(p: Progress, lessons: Lesson[], items: (id: string) => Item, unlockAll: boolean): number {
  if (unlockAll) return lessons.length
  let n = 1
  while (n < lessons.length && lessonMastered(p, lessons[n - 1], items)) n++
  return n
}
