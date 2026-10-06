import { describe, expect, it } from 'vitest'
import { curriculum as c, item, type Curriculum } from '../content'
import { answerOf, makeQuestion, promptOf } from './question'
import { seeded } from './rng'

const none = new Set<string>()

describe('makeQuestion', () => {
  it('always yields 4 unique, unambiguous answers', () => {
    const rng = seeded(1)
    for (const it of c.items)
      for (const mode of ['tib-wylie', 'wylie-tib'] as const) {
        const q = makeQuestion(it, mode, it.kind === 'letter' ? 'letters' : 'syllables', c, none, rng)!
        expect(q.options).toHaveLength(4)
        expect(new Set(q.options.map((o) => answerOf(o, mode))).size).toBe(4)
        expect(q.options[q.correctIndex]).toBe(it)
        const p = promptOf(it, mode, c)
        expect(q.options.filter((o) => promptOf(o, mode, c) === p)).toHaveLength(1)
      }
  })

  it('prefers the same traditional row', () => {
    const q = makeQuestion(item('l-ca'), 'tib-wylie', 'letters', c, none, seeded(2))!
    expect(q.options.map((o) => o.wylie).sort()).toEqual(['ca', 'cha', 'ja', 'nya'])
  })

  it('vowel forms draw distractors from the same base letter', () => {
    const q = makeQuestion(item('v-ki'), 'wylie-tib', 'syllables', c, none, seeded(3))!
    expect(q.options.every((o) => o.baseId === 'l-ka')).toBe(true)
  })

  it('excludes distractors that collide in the prompt (audio equivalence)', () => {
    const withAudio: Curriculum = {
      ...c,
      audioEquivalent: [['ཅ', 'ཆ']],
      items: c.items.map((it) => (it.kind === 'letter' ? { ...it, audio: { file: `${it.id}.mp3`, source: 't', dialect: 't', status: 'approved' } } : it)),
    }
    const ca = withAudio.items.find((x) => x.id === 'l-ca')!
    for (let s = 0; s < 20; s++) {
      const q = makeQuestion(ca, 'audio-tib', 'letters', withAudio, none, seeded(s))!
      expect(q.options.map((o) => o.tibetan)).not.toContain('ཆ')
    }
  })
})
