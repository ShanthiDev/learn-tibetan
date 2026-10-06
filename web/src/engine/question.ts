import { hasAudio, type Curriculum, type Item, type QuizMode } from '../content'
import { shuffle, type Rng } from './rng'

/** Which items may serve as distractors: single letters, or letters + vowel forms. */
export type Scope = 'letters' | 'syllables'

export type Question = { target: Item; mode: QuizMode; options: Item[]; correctIndex: number }

/** Audio identity: the clip, unless curated as indistinguishable from another clip. */
function audioKey(it: Item, c: Curriculum): string {
  const g = c.audioEquivalent.findIndex((grp) => grp.includes(it.tibetan))
  return g >= 0 ? `eq:${g}` : `clip:${it.audio?.file ?? it.id}`
}

export function promptOf(it: Item, mode: QuizMode, c: Curriculum): string {
  return mode === 'tib-wylie' ? it.tibetan : mode === 'wylie-tib' ? it.wylie : audioKey(it, c)
}

export const answerOf = (it: Item, mode: QuizMode): string => (mode === 'tib-wylie' ? it.wylie : it.tibetan)

const inGroup = (lists: string[][], a: string, b: string) => lists.some((l) => l.includes(a) && l.includes(b))

/** Distractor priority tier (lower = better). Spec §6.3. */
function tier(t: Item, d: Item, mode: QuizMode, scope: Scope, c: Curriculum, known: Set<string>): number {
  const visual = inGroup(c.confusables.visual, t.tibetan, d.tibetan)
  const wylie = inGroup(c.confusables.wylie, t.wylie, d.wylie)
  if (scope === 'syllables') {
    if (d.baseId === t.baseId) return 1
    if (d.vowel === t.vowel && d.groupId === t.groupId) return 2
    const base = (it: Item) => c.items.find((x) => x.id === it.baseId)!.tibetan
    if (d.vowel === t.vowel && inGroup(c.confusables.visual, base(t), base(d))) return 3
    return known.has(d.id) ? 4 : 5
  }
  if (d.groupId === t.groupId) return 1
  const [first, second] = mode === 'tib-wylie' ? [wylie, visual] : [visual, wylie]
  if (first) return 2
  if (second) return 3
  return known.has(d.id) ? 4 : 5
}

export function makeQuestion(
  target: Item,
  mode: QuizMode,
  scope: Scope,
  c: Curriculum,
  known: Set<string>,
  rng: Rng,
): Question | null {
  const universe = c.items.filter((it) => (scope === 'letters' ? it.kind === 'letter' : true))
  const p = promptOf(target, mode, c)
  const a = answerOf(target, mode)
  // Ambiguity rule (Spec §6.4): a distractor must differ from the target in prompt AND answer.
  const valid = universe.filter(
    (d) => d.id !== target.id && (mode !== 'audio-tib' || hasAudio(d)) && promptOf(d, mode, c) !== p && answerOf(d, mode) !== a,
  )
  const ranked = shuffle(valid, rng)
    .map((d) => ({ d, t: tier(target, d, mode, scope, c, known) }))
    .sort((x, y) => x.t - y.t)
  const picked: Item[] = []
  const answers = new Set([a])
  for (const { d } of ranked) {
    if (answers.has(answerOf(d, mode))) continue
    picked.push(d)
    answers.add(answerOf(d, mode))
    if (picked.length === 3) break
  }
  if (picked.length < 3) return null
  const options = shuffle([target, ...picked], rng)
  return { target, mode, options, correctIndex: options.indexOf(target) }
}
