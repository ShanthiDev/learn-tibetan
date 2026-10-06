import { describe, expect, it } from 'vitest'
import { curriculum as c, item } from '../content'
import { applyAnswer, emptyProgress, keyOf, lessonMastered, unlockedCount } from './progress'
import { seeded } from './rng'
import { pickNext, type Entry } from './select'

const k = keyOf('l-ka', 'tib-wylie')

describe('progress', () => {
  it('moves boxes up on correct and down on wrong, scheduling a retry', () => {
    const rng = seeded(1)
    let p = applyAnswer(emptyProgress(), k, true, rng)
    p = applyAnswer(p, k, true, rng)
    expect(p.stats[k].box).toBe(2)
    p = applyAnswer(p, k, false, rng)
    expect(p.stats[k]).toMatchObject({ box: 0, seen: 3, correct: 2 })
    expect(p.retry[0].due - p.counter).toBeGreaterThanOrEqual(2)
  })

  it('returns a wrong item after 2-3 questions', () => {
    const rng = seeded(4)
    const pool: Entry[] = ['l-ka', 'l-kha', 'l-ga', 'l-nga'].map((itemId) => ({
      key: keyOf(itemId, 'tib-wylie'), itemId, mode: 'tib-wylie', scope: 'letters', isNew: true,
    }))
    let p = applyAnswer(emptyProgress(), k, false, rng)
    const asked: string[] = []
    for (let i = 0; i < 3; i++) {
      const e = pickNext(pool, p, rng)!
      asked.push(e.key)
      p = applyAnswer(p, e.key, true, rng)
    }
    expect(asked.slice(1)).toContain(k)
  })

  it('unlocks the next lesson once the current one is mastered', () => {
    const rng = seeded(5)
    let p = emptyProgress()
    expect(unlockedCount(p, c.lessons, item, false)).toBe(1)
    for (let i = 0; i < 3; i++)
      for (const id of c.lessons[0].newItemIds) p = applyAnswer(p, keyOf(id, 'tib-wylie'), true, rng)
    expect(lessonMastered(p, c.lessons[0], item)).toBe(true)
    expect(unlockedCount(p, c.lessons, item, false)).toBe(2)
  })
  it('honours a lighter per-lesson mastery bar (share of items)', () => {
    const v3 = c.lessons.find((l) => l.id === 'v3')!
    const rng = seeded(6)
    let p = emptyProgress()
    const ids = v3.newItemIds
    for (const id of ids.slice(0, Math.ceil(ids.length * 0.8) - 1)) p = applyAnswer(p, keyOf(id, 'tib-wylie'), true, rng)
    expect(lessonMastered(p, v3, item)).toBe(false)
    p = applyAnswer(p, keyOf(ids[ids.length - 1], 'tib-wylie'), true, rng)
    expect(lessonMastered(p, v3, item)).toBe(true)
  })
  it('keeps a lesson on topic: earlier lessons only as a ~20 % review share', () => {
    const rng = seeded(7)
    const entry = (itemId: string, isNew: boolean): Entry => ({ key: keyOf(itemId, isNew ? 'audio-tib' : 'tib-wylie'), itemId, mode: isNew ? 'audio-tib' : 'tib-wylie', scope: 'letters', isNew })
    const pool = [...c.items.map((it) => entry(it.id, false)), ...c.items.slice(0, 16).map((it) => entry(it.id, true))]
    let fresh = 0
    for (let i = 0; i < 1000; i++) if (pickNext(pool, emptyProgress(), rng)!.isNew) fresh++
    expect(fresh).toBeGreaterThan(740)
    expect(fresh).toBeLessThan(860)
  })
})
