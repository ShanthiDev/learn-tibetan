# TZ Tibetan → German Phonetics Mapping — Provenance

## Purpose

This mapping is a pragmatic conversion layer from Tibetan-script syllables to the German-readable phonetic spelling used in publications of the Tibetisches Zentrum (TZ).

Its goal is **not** to define a linguistically exact phonemic transcription or a normative pronunciation standard. It is intended to produce an approximate, recognizable TZ-style reading aid for Tibetan practice texts.

The mapping is therefore evidence-based where possible and rule-based where necessary.

## Primary source material

The machine-extracted mapping is based on two publications that contain all three relevant layers:

1. **Kurze tägliche Praxis des Äußerst Geheimen Hayagriva**
   - Tibetisches Zentrum / Tibet-Zentrum Hannover context
   - German translation: Frank Dick
   - Edition visible in source: 2023
   - Contains Tibetan script, German-readable phonetic transcription, and German translation.

2. **Sadhana der Fünf Gottheiten von Heruka Chakrasamvara**
   - Translation: Geshe Pema Samten / Frank Dick
   - Revised through later TZ editions
   - Contains Tibetan script, German-readable phonetic transcription, and German translation.

Other TZ material such as the *Lama Chöpa* and the TZ prayer book was inspected during exploration of the transcription conventions, but was **not used as the principal automatic Tibetan↔phonetic alignment corpus**, because these publications generally do not provide Tibetan script and phonetic transcription side by side.

## Source extraction

The two Sadhanas were processed page by page from rendered PDF images.

OCR was performed on the Tibetan and Latin-script text. The extraction therefore contains OCR errors and should not be treated as a diplomatic transcription of the printed books.

The corpus detected approximately:

- 3,335 Tibetan syllable occurrences
- 822 distinct OCR-derived Tibetan syllable strings

The Tibetan `tsheg` (`་`) was used as the primary syllable boundary.

No attempt was made at this stage to infer Tibetan lexical word boundaries.

## Tibetan ↔ phonetic alignment

Alignment was deliberately conservative.

### Initial alignment

Blocks were used where the number and sequence of Tibetan syllables could be aligned reliably with the corresponding phonetic tokens.

These yielded direct Tibetan-syllable ↔ TZ-phonetic observations.

### Secondary alignment

Additional spans were aligned when they occurred between already established alignment anchors and the Tibetan and phonetic spans had compatible lengths.

These observations are retained separately from the strongest direct alignments so their provenance remains visible.

The resulting v0.1 corpus contained:

- 1,427 aligned Tibetan↔phonetic observations
- 582 distinct Tibetan syllables with at least one observed TZ transcription

These observed mappings cover approximately **88.7% of all Tibetan syllable occurrences** in the extracted corpus, because common syllables recur very frequently.

## Variants and inconsistencies

The TZ material does **not** behave like a completely standardized transcription system.

Different spellings occur:

- between publications,
- occasionally within the same publication,
- and in some cases even for the same Tibetan expression within a short span.

Therefore variants were deliberately preserved rather than normalized away.

Examples include distinctions such as:

- `tschän` / `tchän`
- `tam` / `tham`
- `tschä` / `dschä`
- `tsog` / `tshog`
- `gyi` / `kyi`

Some of these are likely editorial conventions, some contextual pronunciation choices, some simple inconsistencies, and some may be OCR errors.

The corpus therefore stores:

- observed variants,
- their frequencies,
- document-specific modal forms,
- cross-document conflicts,
- and review flags.

In v0.1:

- 27 syllable entries were flagged for cross-document disagreement
- 46 entries showed multiple observed variants

These numbers are indicators for review, not claims that every flagged case represents a genuine linguistic difference.

## v0.2: inferred mappings

The direct corpus did not contain a reliable observation for every distinct OCR-derived Tibetan syllable.

A fallback layer was therefore added in v0.2.

Resolution follows this priority:

1. **Observed TZ transcription**
2. **Curated Sanskrit/mantra exception**
3. **Rule-based Tibetan orthography → approximate TZ-style phonetics**
4. **Unresolved / probable OCR noise**

Observed TZ evidence always takes precedence over generated forms.

### Rule-based inference

Missing Tibetan syllables were approximately pronounced by decomposing Tibetan orthographic syllable structure, including where identifiable:

- prefix
- superscribed consonant
- root consonant
- subscribed consonant
- vowel
- suffix
- second suffix

The rule design was informed by the general architecture of existing Tibetan grapheme-to-phonetics systems, particularly the open-source `tibetan-to-phonetics` project.

The generated output was adapted toward the spellings observed in the TZ corpus, e.g. German-oriented forms such as:

- `tsch`
- `dsch`
- `sch`
- `gy`
- `ny`
- `ä`
- `ö`
- `ü`

The implementation in v0.2 is our own lightweight approximation; it is **not a verbatim copy of the external library's output**.

Reference implementation consulted:

- https://github.com/jerefrer/tibetan-to-phonetics

## Sanskrit and mantra material

Sanskrit/mantra syllables require separate treatment because ordinary Tibetan pronunciation rules are not sufficient.

A small set of explicit exceptions was therefore added for forms occurring commonly in the source material, for example:

- `བཛྲ` → `BENDSA`
- `ཧཱུཾ` → `HUNG`
- `གནྡྷེ` → `GHÄNDE`
- `སྭཱཧཱ` → `SOHA`

These reflect approximate TZ practice-text spelling rather than scholarly Sanskrit transliteration.

They should eventually be moved into a dedicated Sanskrit/mantra lexicon.

## Coverage after inference

The v0.2 mapping contains 822 distinct OCR-derived Tibetan syllable strings.

Of these:

- 582 have direct TZ-derived mappings
- 226 received inferred fallback mappings
- 808 therefore currently have a usable phonetic output
- 14 remain unresolved or classified as probable OCR noise

Thus almost all syllable types encountered in the two source texts have a usable fallback, while direct and inferred evidence remain distinguishable.

## Important data fields

The mapping intentionally preserves provenance.

Relevant fields include:

- `tibetan_syllable`
- `hayagriva_mode`
- `chakrasamvara_mode`
- `overall_mode`
- `variants`
- `aligned_observations`
- `exact_observations`
- `anchor_inferred_observations`
- `cross_document_conflict`
- `generic_rule_output`
- `resolved_tz_phonetic`
- `resolution_origin`
- `resolution_confidence`
- `resolution_note`

`resolved_tz_phonetic` is the practical value intended for downstream use.

`resolution_origin` is particularly important and should not be discarded. It distinguishes values such as:

- `observed_TZ`
- `inferred_exception`
- `inferred_rule_tibetan`
- `inferred_rule_sanskrit`
- `ocr_noise`
- `unresolved`

## Recommended interpretation

The mapping should be treated as:

> an approximate, auditable TZ-style pronunciation layer

rather than:

> an authoritative Tibetan pronunciation dictionary.

For display and reading assistance this distinction is usually irrelevant. For linguistic analysis, phonology, dialectology, or reconstruction of exact spoken Tibetan it matters considerably.

## Word segmentation

The current mapping operates primarily at the Tibetan **syllable** level.

This matches the structure of the source TZ transcriptions fairly well, because TZ practice texts generally print Tibetan pronunciation syllable by syllable.

A future word-segmentation layer should therefore remain separate from the pronunciation mapping.

Recommended internal representation:

    Tibetan text
        ↓
    Tibetan syllables
        ↓
    word segmentation
        ↓
    phonetic mapping per syllable
        ↓
    renderer

For example:

    བྱང་ ཆུབ་ | སེམས་ ཅན་

can retain four independently mapped syllables internally while allowing two display modes:

    recitation view:
    dschang tschub sem tschän

    word-learning view:
    dschangtschub semtschän

Word boundaries should therefore be metadata/structure rather than being baked permanently into the phonetic strings.

This also allows later word-level exceptions where connected pronunciation differs from naïvely concatenating individual syllables.

## Known limitations

1. **OCR noise**
   - Tibetan OCR is imperfect.
   - Rare syllables are disproportionately likely to contain OCR errors.

2. **Alignment uncertainty**
   - Not every Tibetan↔phonetic pair was manually verified.
   - Some alignments were inferred from surrounding anchors.

3. **TZ inconsistency**
   - The source publications themselves contain variant spellings.
   - There is no evidence for one completely rigid TZ transcription standard.

4. **Dialect / pronunciation model**
   - The system approximates the central/literary Tibetan pronunciation underlying these Gelug practice texts.
   - It does not model regional Tibetan dialects.

5. **Context sensitivity**
   - A simple syllable dictionary cannot capture every phonological effect.
   - Future rules may need neighbouring syllables, lexical word identity, or word position.

6. **Sanskrit**
   - Sanskrit and mantra material currently uses a small exception layer.
   - This should eventually become a dedicated subsystem.

7. **Not a scholarly transliteration**
   - This mapping must not be confused with Wylie/EWTS, THL transliteration, or IPA.
   - It represents pronunciation-oriented German respelling.

## Suggested refinement strategy

Future refinement should preserve the existing evidence rather than overwrite it.

Recommended order:

1. correct obvious OCR errors;
2. add further TZ texts containing both Tibetan and phonetic transcription;
3. accumulate observations rather than replacing variants;
4. distinguish document/editor-specific conventions where useful;
5. add Tibetan word segmentation;
6. introduce context-dependent pronunciation rules only where corpus evidence requires them;
7. maintain a separate Sanskrit/mantra lexicon;
8. keep generated and directly attested forms distinguishable.

A useful long-term model is therefore not simply:

    tibetan_syllable → phonetic_string

but:

    pronunciation(
        syllable,
        word=None,
        previous_syllable=None,
        next_syllable=None,
        source_profile="tz",
    )

with corpus-backed defaults and explicit overrides.

## Generated artifacts

The initial work produced:

- `TZ_Tibetan_Phonetics_Corpus_v0.2_resolved.xlsx`
  - human-readable corpus, variants, review flags and provenance

- `TZ_tibetan_phonetics_mapping_v0.2_resolved.csv`
  - tabular mapping

- `TZ_tibetan_phonetics_mapping_v0.2_resolved.json`
  - machine-readable mapping intended for pipeline integration

- `TZ_tibetan_phonetics_observations_v0.1.csv`
  - raw aligned Tibetan↔phonetic observations used as evidence

The original observation corpus should also be retained whenever possible, because it is the evidence from which normalized mappings can later be regenerated.

## Reproducibility principle

The mapping should not be treated as primary evidence.

The intended hierarchy is:

    source PDFs
        ↓
    OCR / extracted observations
        ↓
    aligned observation corpus
        ↓
    normalization + inference rules
        ↓
    resolved mapping

In other words:

> The observations are the evidence; the mapping is a compiled artifact.

Any future refinement should ideally modify the source observations, OCR corrections, or inference rules and then regenerate the mapping rather than manually editing unexplained final values.
