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
})
