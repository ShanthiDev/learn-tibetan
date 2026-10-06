import raw from './curriculum.json'

export type QuizMode = 'tib-wylie' | 'wylie-tib' | 'audio-tib'
export type VowelId = 'a' | 'i' | 'u' | 'e' | 'o'

export type Analysis = {
  prefix: string | null
  superscript: string | null
  root: string
  subscripts: string[]
  vowel: string
  suffix: string | null
  postsuffix: string | null
}

export type AudioRef = { file: string; source: string; dialect: string; status: 'candidate' | 'approved' }

export type Item = {
  id: string
  kind: 'letter' | 'vowel-form'
  tibetan: string
  wylie: string
  tz: string
  order: number
  groupId: string
  baseId: string
  vowel: VowelId
  devanagari?: string
  devanagariNote?: string
  analysis: Analysis
  audio?: AudioRef
}

export type Group = { id: string; order: number; labelDe: string; linguistic?: string; itemIds: string[] }

export type Lesson = {
  id: string
  chapter: 1 | 2 | 3 | 4 | 5
  titleDe: string
  introItemIds?: string[]
  newItemIds: string[]
  modes: QuizMode[]
  mastery?: { box: number; share: number } // default: every item/mode at CONFIG.masteredBox
}

export type Curriculum = {
  meta: { engine: { tz: string; wylie: string; tzVariant: string } }
  alphabetNoteDe: string
  vowels: { id: VowelId; sign: string; nameDe: string }[]
  groups: Group[]
  items: Item[]
  lessons: Lesson[]
  confusables: { visual: string[][]; wylie: string[][] }
  audioEquivalent: string[][]
}

export const curriculum = raw as unknown as Curriculum
export const itemsById = new Map(curriculum.items.map((it) => [it.id, it]))
export const groupsById = new Map(curriculum.groups.map((g) => [g.id, g]))
export const item = (id: string): Item => itemsById.get(id)!
/** Only curated clips are used for learning; candidates are heard in the review screen only. */
export const hasAudio = (it: Item) => it.audio?.status === 'approved'

export const CHAPTERS: Record<number, string> = {
  1: 'Das Alphabet als System',
  2: 'Zeichen → Wylie',
  3: 'Wylie → Zeichen',
  4: 'Vokale',
  5: 'Hören',
}
