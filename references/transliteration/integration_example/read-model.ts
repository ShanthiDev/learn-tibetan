/**
 * Publication Read Model v2.3.
 *
 * This is a deterministic, display-oriented projection. It is not canonical ATP and it is not a
 * write contract. Array order is reading order; strings are plain Unicode. Text selectors count
 * Unicode code points (not UTF-8 bytes or JavaScript UTF-16 code units).
 */
export type BlockKind = 'prose' | 'verse' | 'rubric' | 'mantra' | 'heading' | 'paratext' | 'source'

export type Block = {
  id: string
  kind: BlockKind
  text: string
  repeat?: string
  iast?: string
  note?: string
}

export type StylePolicyDisplay = { label: string; terminology?: string }

export type TranslationLayer = {
  id: string
  language: string
  mode: string
  label: string
  description: string
  edition_ids: string[]
  style_policy?: StylePolicyDisplay
  attribution_ids: string[]
}

export type EditionDecision = {
  id: string
  label: string
  statements: string[]
  exceptions: string[]
  levels: string[]
  scope_note?: string
}

/** A citable reading version. Every edition selects exactly one translation per passage and layer. */
export type Edition = {
  id: string
  label: string
  language: string
  status: string
  translation_layer_ids: string[]
  note: string
  recorded_at?: string
  history?: {
    based_on_edition_id: string
    changed_passage_ids: string[]
    question_ids: string[]
    applications: string[]
    decisions: EditionDecision[]
  }
}

export type Attribution = {
  id: string
  kind: 'model' | 'agent_workflow' | 'human' | 'organization'
  label: string
  detail?: string
}

export type AttributionLinks = {
  attributed_to?: string[]
  recorded_by?: string[]
  derived_from_attribution_ids?: string[]
}

export type ReferenceTarget = {
  id: string
  kind: 'house_decision'
  label: string
  preview: string
  status: string
  attribution?: AttributionLinks
}

export type TextSelector = {
  type: 'text_position'
  coordinate_system: 'unicode_code_points'
  start: number
  end: number
  quote: string
}

export type Target = {
  id: string
  passage_id: string
  scope: 'passage' | 'source' | 'translation'
  translation_layer_id?: string
  block_id?: string
  selector?: TextSelector
}

export type Annotation = {
  id: string
  family: 'recitation' | 'diplomatic'
  kind: 'decision' | 'alternative' | 'addition' | 'omission' | 'diplomatic_note' | 'diplomatic_alternative'
  category?: string
  text: string
  alternatives: string[]
  target_ids: string[]
  source_id: string
  source_status: string[]
  reference_ids: string[]
  attribution?: AttributionLinks
}

export type Question = {
  id: string
  kind: 'curated_question' | 'reviewer_request'
  label?: string
  request?: 'decision' | 'comment' | 'information'
  addressed_to?: string[]
  options?: { label: string; text: string }[]
  /** Absent: shown in every edition. */
  edition_ids?: string[]
  text: string
  status: string
  primary_target_id: string
  target_ids: string[]
  related_issue_ids: string[]
  source_id: string
  source_status: string[]
  reference_ids: string[]
  attribution?: AttributionLinks
}

export type Issue = {
  id: string
  kind: 'diplomatic_issue'
  text: string
  status: string
  target_ids: string[]
  related_question_ids: string[]
  source_id: string
  source_status: string[]
  attribution?: AttributionLinks
}

export type PassageTranslation = {
  layer_id: string
  /** The editions that show exactly this translation. */
  edition_ids: string[]
  /** Set for post-v10 candidates selected by an edition. */
  candidate_id?: string
  blocks: Block[]
  source_status: string[]
  attribution?: AttributionLinks
}

export type SourceContent = { id: string; language: string; blocks: Block[] }

export type MeaningSketch = {
  translation_layer_id: string
  summary: string
  practice?: string
  concepts?: string
  source_status: string[]
  attribution?: AttributionLinks
}

export type PronunciationVariant = {
  id: string
  label: string
  description: string
  default: boolean
}

export type PronunciationAid = {
  id: string
  language: string
  status: 'generated'
  generator: { name: string; version: string }
  source_block_id: string
  variants: { variant_id: string; lines: { tibetan: string; pronunciation: string }[] }[]
}

export type Transliteration = {
  id: string
  scheme: 'ewts'
  status: 'generated'
  generator: { name: string; version: string }
  source_block_id: string
  lines: { tibetan: string; text: string }[]
}

export type Passage = {
  id: string
  source: SourceContent
  translations: PassageTranslation[]
  meaning?: MeaningSketch
  pronunciation?: PronunciationAid
  transliteration?: Transliteration
}

export type Publication = {
  version: '2.3'
  id: string
  release: { id: string; source_bundle_sha256: string }
  metadata: { title: string; subtitle: string; edition_note: string }
  editions: Edition[]
  default_edition_id: string
  pronunciation_variants: PronunciationVariant[]
  translation_layers: TranslationLayer[]
  attributions: Attribution[]
  references: ReferenceTarget[]
  targets: Target[]
  annotations: Annotation[]
  questions: Question[]
  issues: Issue[]
  sections: { id: string; title: string; passages: Passage[] }[]
}

export function translationFor(passage: Passage, layerId: string, editionId: string): PassageTranslation | undefined {
  return passage.translations.find(translation => translation.layer_id === layerId && translation.edition_ids.includes(editionId))
}
