import { expect, it } from 'vitest'
import { applyAnswer, emptyProgress } from './engine/progress'
import { seeded } from './engine/rng'
import { load, save } from './storage'

it('round-trips progress through localStorage', () => {
  const mem = new Map<string, string>()
  globalThis.localStorage = { getItem: (k: string) => mem.get(k) ?? null, setItem: (k: string, v: string) => mem.set(k, v) } as unknown as Storage
  const p = applyAnswer(emptyProgress(), 'l-ka|tib-wylie', true, seeded(1))
  save('lt.v1.progress', p)
  expect(load('lt.v1.progress', emptyProgress())).toEqual(p)
})
