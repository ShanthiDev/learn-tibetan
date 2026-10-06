# Phonetics 01 — Exploratory TZ-style German phonetic generator

**Created:** 2026-09-25T15:59:07+02:00
**Last updated:** 2026-09-25T19:01:52+02:00
**Status:** draft (planning-phase research; not integrated)
**Origin:** repository_agent_generated
**Document role:** research_report

## Scope

The owner asked for a planning-phase exploration: write a procedural Tibetan → German (TZ-style)
phonetic generator, run it over real source text, measure the gaps, collect unknown mappings in
a separate document with proposed transcriptions, and spot-check the plausibility of the
externally prepared TZ mapping. This is explicitly **not** Reader/Workbench integration. No
Reader, PRM, projector or authoring code changed.

Branch `task/hayagriva-reader-mvp`, base `39d3ad7`.

## Inputs

| Input | Role |
|---|---|
| `data/reference_phonetics/TZ_tibetan_phonetics_mapping_v0.2_resolved.json` (+ `.csv`, `_PROVENANCE.md`) | Owner-supplied mapping prepared by another agent outside this repository from OCR of two TZ sadhanas (Hayagriva short practice, Frank Dick 2023; Chakrasamvara five deities). 822 syllable strings. **Untracked in Git at the time of this report.** The raw observation corpus and XLSX named in its provenance note are not present. |
| `web/hayagriva-reader/src/generated/publication.json` | Test corpus: Tibetan source blocks of all 192 Hayagriva passages (11,875 syllable tokens, 1,432 types after tokenisation). |
| The six `unreviewed-example` Reader pronunciation aids (20 lines) | Comparison only. They are assistant-written, not gold. |
| `jerefrer/tibetan-to-phonetics` (MIT, cloned to scratch only) | Consulted for rule architecture. It has no German ruleset. No code copied. |

## What was built

`scripts/phonetics_research/tz_phonetics.py` is a self-contained research module. It resolves each
syllable in this order and records the origin:

1. `override`: hand-curated values (the `overrides.json` hook exists but is empty).
2. `mantra_exception`: a built-in seed-syllable/mantra lexicon (OM, HUNG, HRIH, PHE, BENDSA,
   SOHA, PEMA, …) plus the mapping's `inferred_exception` entries.
3. TZ evidence cross-checked against the rules:
   - `confirmed`: at least one plausible TZ observation agrees with the rule output, allowing
     for differences in convention.
   - `observed_TZ`: the rule disagrees, but a plausible observation occurs ≥2 times and outnumbers
     the agreeing ones (≥3 if the coda contradicts the orthography).
   - `rule_contested`: the only observations are single disagreeing ones. The rule output is
     kept and the case is flagged.
4. `rule_tibetan`: an orthographic parser (prefix / superscript / root / subscripts / vowel /
   suffix / post-suffix / fused particles འི འོ འུ འང འམ) with a TZ-Hayagriva profile. Examples:
   ཅ/ཆ tsch, ཇ dsch, ཞ/ཤ sch, ཚ tsh, aspirates th/kh/ph, ཡ-subscript on p/ph/b → tsch/tsch/dsch,
   ར-subscript → tr/thr/dr, དབ → w, དབྱ → y, umlaut before ད ས ན ལ and genitive འི, mute ད/ས.
5. `rule_sanskrit`: a mantra transliteration into TZ-like capitals, used for syllables that are
   not well-formed Tibetan. Sanskrit loans in Tibetan prose are lower-cased.

The generator also handles these phrase-level cases:
- Phrases are split at shad or gter-tsheg. Physical line breaks are not treated as phrase breaks.
- Mantra phrases (share of Sanskrit syllables ≥ 0.4) are upper-cased. Tibetan-looking syllables
  inside them are re-read with the Sanskrit rules.
- Visarga/anusvara glued without a tsheg is split.
- Source tokens with a missing tsheg (གཡསགཉིས) are split into two valid syllables.

`scripts/phonetics_research/evaluate.py` regenerates every artifact below.

## Results

Artifacts: `data/derived/phonetics-research/`
(`summary.json`, `mapping-audit.csv`, `gap-review.md`, `gap-syllables.csv`,
`hayagriva-generated.{txt,json}`, `reader-example-comparison.json`).

### Corpus coverage (192 passages, 11,875 tokens)

| Origin | Tokens | Share | Types |
|---|---:|---:|---:|
| confirmed (rule = TZ evidence) | 7,903 | 66.6 % | 433 |
| mantra_exception | 729 | 6.1 % | 52 |
| observed_TZ (evidence overrides rule) | 63 | 0.5 % | 4 |
| rule_contested | 176 | 1.5 % | 21 |
| rule_tibetan (no evidence) | 2,446 | 20.6 % | 737 |
| rule_sanskrit (no evidence) | 558 | 4.7 % | 185 |
| unresolved | 0 | 0 % | 0 |

Every token gets a proposal. About 73 % of tokens are backed by TZ evidence or the curated mantra
lexicon. The remaining ~27 % are rule-generated. These fall into 943 types, mostly low-frequency
ones: 737 Tibetan and 185 Sanskrit rule types, plus 21 contested.

### Manual review of the gap list

I read through the ~260 most frequent `rule_tibetan` types (over 80 % of those tokens) and the
first ~90 `rule_sanskrit` types. I found no systematic Tibetan rule error that is still open.
Examples: གཏོར tor, བསྲུང sung, བརྒྱུད gyü, འབུལ bül, མཛོད dzö, དགྲ dra, བསྐངས kang,
བཟླས dä, བརླབས lab, རྫོགས dzog, ལྗང dschang, དབུ་སྐྲ u tra. The errors found during review were
fixed in the generator: དབྱ → y, the reversed gigu as a Sanskrit marker, long vowels with a vowel
sign (ཨཱོཾ → OM), inherent vowels in conjuncts, and casing of loans in prose.

### Comparison with the six Reader examples (20 lines)

The generator reproduces the earlier hand-written examples almost exactly. It differs only in
these places:
- ཁྲོས `thrö` (example `tröp`)
- ཚ `tshe` (example `tse`)
- ཟླ་བར `da war` (example `da bar`)
- རྫོགས `dzog` (example `dsog`)
- ཤོག `scho` (example `schog`, see open question 1)
- mantra lines, which the generator upper-cases and splits per syllable (`SA MA YA`)

Neither side is gold.

### Mapping plausibility audit

**Observed layer (582 entries).** Under convention-insensitive comparison, the rule engine agrees
with at least one plausible TZ observation for 488 of 544 comparable Tibetan entries (89.7 %). The
mapping's own `generic_rule_output` agrees for 464 (85.3 %). The rules were refined while looking
at this evidence, so 89.7 % is an in-sample figure, not a held-out accuracy.

The observed layer is usable as evidence. Its compiled value `resolved_tz_phonetic` should not
be used directly:

1. **The Hayagriva mode always wins, even against clear majorities.** In all 19 cases where
   `resolved` ≠ `overall_mode`, the resolved value equals the Hayagriva mode. Examples:
   ལས `IG` (lä:3), བཀྲ `ta` (tra:3), གིས `gyi` (gi:8), གྱི `gi` (gyi:5, so the two are
   swapped), རྒྱས `gyda`, ཀའི `kd`, དྲག `dag`.
2. **Latin OCR noise survives into resolved values.** Examples: ལྷ `Iha`, གནས `nd`, ནུས `nU`,
   རྒྱན `gyGn`, བསྐལ `kdl`, དུད `dt`. OCR dropping the umlaut dots also skews counts:
   པའི pa:15 vs pä:5 (+ pd/pad/pda), and པས, དུས, གདན, རྣལ follow the same pattern.
3. **Tibetan OCR noise in the keys.** Many keys are misread syllables whose phonetic value belongs
   to the intended syllable. Examples: པའེ for པའི, གཉེས for གཉིས, གྱར for གྱུར, ནེ for ནི,
   སྟོམས for སྙོམས, སྒྱེས for སྐྱེས, སྐོང for སྐྱོང, རྭུ for ཧཱུཾ. Most never match clean text.
   Some collide with real syllables and would poison them (ནེ → ni, ཐོ → tschig, ཆུ has a ru
   observation). This is why a single disagreeing observation never overrides the rules here.
4. **Single-observation alignment shifts.** Examples: ཐོ `tschig`, ཁོད `thrö`, ཐག `trag`,
   དྲུན `darin`, སྙུག `dug`, ཝུ `aus`.
5. **Two TZ conventions are mixed.** The Hayagriva booklet writes ཚ as `tsh` and aspirates as
   `th/kh/ph`. The Chakrasamvara text mostly writes `z/ze/zog` and sometimes unaspirated `t/k/p`.
   The generator normalises to the Hayagriva profile. It treats the other spellings as equivalent
   evidence, not as contradictions.

After these corrections, 150 of the 582 compiled observed values differ from the generator's
decision:

| Kind of difference | Count |
|---|---:|
| contested single observations replaced by the rule output | 67 |
| umlaut restoration | 22 |
| Sanskrit entries not compared (skipped) | 21 |
| convention normalisation | 17 |
| majority repair / other | 16 |
| OCR-noise values removed | 5 |
| other (case, evidence override) | 2 |

**Inferred layer (240 entries).** 129 of 167 `inferred_rule_tibetan` entries agree with the
generator. The disagreements include real rule defects:
- devoicing inherited from an English-style ruleset (ག ka, གེ ke; the observed TZ evidence
  writes gi/gang)
- dropped aspirate consonants (དྷ `ha`, དྷུ `hu`, དྷུཔེ `hu`)
- whole Sanskrit words collapsed to one syllable (སཏྭ `ta`, ཁནྟ `ta`, ཧོབཛྲ `dsob`)
- OCR-garbled multi-syllable keys reduced to their first syllable

The inferred layer should be treated as **superseded by a proper rule engine**, not as evidence.

**Verdict.** The other agent did useful, honest work: provenance is preserved, variants are kept
and the uncertainty is documented. The *observed variant counts* are the valuable part. The
*resolution policy* and the *inferred fallback* are too weak to feed a Reader directly.

## Open questions for the owner

1. **ཤོག: `scho` or `schog`?** The evidence says scho:8 / schog:1, all from the Chakrasamvara
   text. The generator currently follows the evidence. The Reader example used `schog`.
2. **Target convention.** Should `tsh`, `th`, `kh` and `thr` follow the TZ Hayagriva booklet (the
   current default), or `z`, `t` and `tr` as in the Chakrasamvara text? One profile switch covers
   this.
3. **Word joining.** TZ texts sometimes join words (`pema`, `dorsche`?). The generator emits
   syllables. The mapping's provenance note already recommends keeping word boundaries as
   separate metadata.
4. **Mantra rendering.** Should mantras be all caps with one syllable per token (`SA MA YA`), or
   joined (`SAMAYA`)?
5. **The raw observation corpus.** The provenance names `TZ_tibetan_phonetics_observations_v0.1.csv`
   and an XLSX. Neither is here. With them (ideally with document and line IDs), the Hayagriva
   booklet could become a real held-out test set.

## Proposed plan (not yet authorised)

1. Owner answers the questions above. A Tibetan-literate reviewer then corrects the ~150 most
   frequent `rule_tibetan` / `rule_sanskrit` types in `gap-review.md` through `overrides.json`.
   That covers most of the gap tokens.
2. Obtain the raw observations. Build a held-out evaluation, for example training on the
   Chakrasamvara text and testing on the Hayagriva text. Report syllable accuracy honestly.
3. Add a small word-level exception layer: རྡོ་རྗེ dor dsche, བཅོམ་ལྡན་འདས, and seed-syllable
   compounds. Add a word-boundary layer as metadata, not as baked-in strings.
4. Only then, as a separate authorised task, integrate it: generate `phonetic_de` per passage with
   status `generated-draft`, keep the per-syllable origin for audit, keep the Reader's existing
   pronunciation contract (outside translation layers, lines concatenating to the exact source),
   and have the Reader show a draft label.

## Remaining uncertainty

- No gold TZ transcription of *this* Hayagriva text exists in the repository. Agreement with TZ
  evidence is measured per syllable type, not on running text.
- The rule profile is my own synthesis of TZ practice. The judgements in the manual review are
  assistant judgements, not owner or TZ review.
- Context effects (voicing after nasals, word-internal `b → w` beyond particles, contextual `dor`)
  are only modelled where evidence forced it.

## Follow-up 2026-09-25T16:54:30+02:00 — source OCR, observation cross-check, held-out test

The owner added the Excel corpus (with a per-observation sheet: document, page, block, positions)
and three primary PDFs to `data/reference_phonetics/`: the Hayagriva short practice (16 pp.), the
Chakrasamvara sadhana (52 pp.) and the TZ Gebetsbuch (37 pp.; German plus Tibetan phonetics only,
decades in use). The Lama Chöpa PDF is absent (only its `Zone.Identifier`). The PDFs are image-only
scans. The owner installed Tesseract 5.3.4 (`deu`, `bod`). All 105 pages were OCR-ed locally
(300 dpi, `deu`, `--psm 4`). Model tokens were spent only on reading summaries and samples.

New research helpers in `scripts/phonetics_research/`:
- `tz_ocr_lines.py` extracts the phonetic lines from the OCR output.
- `crosscheck_observations.py` aligns the other agent's observations page by page with our OCR.
- `heldout_eval.py` runs the held-out test against `gebetsbuch_heldout.tsv`.

Outputs are in `data/derived/phonetics-research/`: `ocr/`, `observation-crosscheck.csv` and
`gebetsbuch-heldout.txt`.

### 1. Independent re-OCR of the external observation corpus

Of 1,427 observations, 1,163 could be aligned position-wise with our OCR. **1,092 (93.9 %) are
identical.** 71 differ and 264 are unaligned. 35 of the 71 differences are umlaut loss on the other
agent's side (`pa`→`pä` ×13, `wa`→`wä`, `dan`→`dän`, …). Most of the rest are garbage
tokens that our OCR reads cleanly (`gyda`→`gyä`, `nd`→`nä`, `gyGn`→`gyän`, `darin`→`drin`).
A few are Tesseract's own errors (`tnam`, `asche`).

This upgrades several earlier inferences to **confirmed on the page**: umlaut loss inflating
`pa` over `pä`, and garbage variants such as `gyda`, `nd`, `kd` and `gyGn`. The ཐོ → `tschig`
misalignment is confirmed from the corpus's own metadata: Tibetan position 16 was paired with
phonetic position 3.

Two earlier claims are **corrected**:
- `Iha` is read identically by both OCR engines. The printed font does not distinguish l and I.
  The intended value is `lha`, but it is not the other agent's misreading.
- The "Hayagriva writes tsh, Chakrasamvara writes z" hypothesis is wrong. The Hayagriva booklet
  itself prints both `tshog` (p. 5) and `Iha zog` (p. 12), `drub par scho` (p. 5) and
  `ta schi schog` (p. 12), and `pal den` without umlaut (p. 7). TZ spelling is not internally
  uniform even within one booklet. `kan drin` (p. 7) versus `khadro` (p. 12) shows that
  nasalisation before a following prefixed syllable is also applied inconsistently. The coda filter
  that rejected such forms (`khan`) was therefore too strict.

### 2. Held-out test against the TZ Gebetsbuch

The Gebetsbuch shows one consistent older convention: aspiration unmarked (`tsog`, `tam tschä`,
`kor`, `pän`), ཛ written `ds` (`dsin`, `dsä`), ཤོག always `scho` (5:0). A second switchable
profile, `gebetsbuch`, was added. The default profile, `hayagriva`, keeps `tsh/th/kh/ph/dz`.

The Gebetsbuch prints no Tibetan. For 64 lines of well-known liturgy (refuge and bodhicitta, the
King of Prayers verses 1–12, mandala offering, general confession), the Tibetan was reconstructed
**from the assistant's memory**. That reconstruction is unverified, and a reconstruction error
counts against the generator. The rules were never tuned on this source.

| Profile | TZ tokens identical |
|---|---:|
| `hayagriva` | 522 / 566 (92.2 %; almost all differences are the aspiration convention) |
| `gebetsbuch` | **551 / 566 (97.3 %)** |

Results are identical with and without the mapping evidence, so the rule engine carries the result.

Remaining differences (gebetsbuch profile):
- genitive after u/o is not umlauted: `tschu` ×3, `tso`
- ཅི: `tschi` ×2, where the Chakrasamvara evidence majority forced `dschi`
- `wa` for བར before a verb ×2
- `sching` where the reconstruction has ཅིང ×2
- `nab sa` (the prefix of the next syllable heard as a coda)
- `la` for ལྷ
- `gyi`/`kyi` once
- one OCR error (`jü`)
- one reconstruction/print difference (`rim pa`/`par`)

**Interpretation.** Gross errors (a wrong syllable identity) did not occur in the held-out sample.
The residual differences are convention and sandhi details, several of which TZ itself applies
inconsistently.

### Consequences

- Two conventions exist and TZ has probably evolved: the older, consistent prayer book versus the
  newer, mixed 2023 booklet. The generator now carries both as switchable profiles. Which one the
  Reader uses by default is a product decision for the owner. It needs no Tibetan knowledge.
- The observation corpus should be regenerated from the new OCR rather than patched. Evidence
  decisions should use the 1,092 cross-confirmed observations.
- Candidate refinements, each supported by held-out or page evidence:
  - a genitive-umlaut switch per profile
  - particle ཅིང/ཞིང/ཤིང handling
  - optional sandhi rules (nasalisation, prefix-as-coda), off by default because TZ applies them
    inconsistently
  - relaxing the coda filter


## Follow-up 2026-09-25T19:01:52+02:00: production generator and Reader integration

The research module was ported to `src/atp/phonetics/tz.py`. The port has no dependency on the
mapping, uses explicit switches and variants, and is covered by 36 unit tests. At owner request,
mantras are **not** special-cased: every syllable is read on its own, in lower case. Held-out
Gebetsbuch test (566 TZ tokens, Tibetan side assistant-reconstructed):

| Variant | Identical tokens |
|---|---:|
| tz-gebetsbuch | 557 (98.4 %; previously 97.3 %) |
| tz-aktuell | 524 (92.6 %) |
| silbengetreu | 522 (92.2 %) |

The improvement comes from ཅི *tschi* and the genitive switch. Across the Hayagriva corpus
(11,875 syllables), `tz-gebetsbuch` differs from `tz-aktuell` in 1,191 syllables and
`silbengetreu` in 242.

The scripts in `scripts/phonetics_research/` remain the frozen research snapshot. They still
import their own module and are not the production path. For the current-state explanation in
German, see `docs/tz-umschrift.md`.
