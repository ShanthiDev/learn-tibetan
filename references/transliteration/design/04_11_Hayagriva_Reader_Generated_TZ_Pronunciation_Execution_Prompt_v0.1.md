# 04_11 — Hayagriva Reader: generated TZ pronunciation with switchable conventions

**Created:** 2026-09-25T17:33:44+02:00
**Last updated:** 2026-09-25T19:01:52+02:00
**Status:** executed (2026-09-25T19:01:52+02:00) with owner revisions during execution; see §10. The original text below is kept unchanged.
**Origin:** repository_agent_generated
**Document role:** execution_prompt
**Builds on:** `docs/research/phonetics-01-tz-generator-exploration.md`,
`docs/research/phonetics-01-erklaerung-methodik-und-stand.md`
**Branch:** `task/hayagriva-reader-mvp`

---

## 0. Instructions for the executing agent

You are integrating the exploratory TZ phonetics generator into the Hayagriva Reader. Before you
start, read `AGENTS.md`, the Compass v0.5.0 sections on the Reader and the PRM, the two phonetics
reports named above and `web/hayagriva-reader/README.md`. Read each only as far as the task needs
(Compass §2.5: token-aware). Do not repeat the research. Its measurements are reusable evidence
unless an input changes.

Work: **inspect enough → decide → build → test → show → stop.** Do not commit until the owner asks.

## 1. Owner decisions (2026-09-25)

| # | Decision | Status |
|---|---|---|
| D1 | The Reader gets a **convention switch**. Both conventions are **pre-generated at build time**. There is no generation in the browser. | decided |
| D2 | Mantras are rendered **syllable by syllable** (`SA MA YA`), generated from the Tibetan. Do **not** extract or copy mantras from the German recitation text. Differences from its mantra spelling are acceptable and informative. | decided |
| D3 | The Reader label says **"automatisch erzeugt"**, without "ungeprüft". | decided |
| D4 | The six hand-written `unreviewed-example` aids are replaced by the generated output. | decided (owner approved the plan) |
| D5 | Default convention `tz-aktuell`, labelled "TZ aktuell" (Hayagriva booklet 2023, aspiration marked). Second convention `tz-gebetsbuch`, labelled "TZ Gebetsbuch" (aspiration unmarked). | decided (owner: "Voreingestellt ist TZ aktuell") |
| D6 | After execution, write a German current-state document on how the generator works and why it can be trusted. Focus on function and trust; the genesis gets only a short mention. It explains the sounds and the two conventions exhaustively, including the relation to Devanagari, for readers who do not read Tibetan. It supersedes `phonetics-01-erklaerung-methodik-und-stand.md`. | decided |

## 2. Scope

**In scope:**
- a production generator module;
- the corrections listed in §4;
- tests;
- a small change to the Publication Read Model (PRM) contract;
- the projector integration;
- the Reader switch;
- updates to README, report, engineering log and CHANGELOG.

**Out of scope:**
- word joining;
- general sandhi rules;
- a review or override UI;
- pronunciation inside the Workbench;
- audio;
- other languages;
- regenerating the external observation corpus;
- committing the TZ source PDFs.

## 3. Architecture

```
Tibetan source blocks (v10 bundle, via the existing projector)
      ↓
src/atp/phonetics/tz.py        stdlib only; deterministic; no build-time dependency on
      ↓                         data/reference_phonetics/ (the held-out test showed no benefit)
convert_sample.py              writes both conventions per passage into publication.json
      ↓
Reader                         displays; the switch selects the convention; no Tibetan logic in TS
```

The projector already imports from `src/atp/` (`sys.path` insert). Put the generator there. The
research scripts in `scripts/phonetics_research/` remain research tools. Point them at the new
module where that is trivial. Otherwise leave them as they are and say so in the report.

Remove the projector's `--phonetics` / `fixtures/sample.json` pronunciation path completely. Keep
the fixture file as history (Compass §2.2: no legacy bridges).

## 4. Generator corrections to carry out during the port

Each correction is backed by evidence in the phonetics reports:

1. **Remove the implicit mapping overrides.** Replace them with an explicit, commented exception
   table that records the evidence for each entry:
   - `རྡོ` + following `རྗེ*` → `dor`. This is a **word rule**, not a syllable override: the
     superscript ར of རྗེ is heard at the end of the previous syllable. Evidence: dor:12 in the
     mapping. All 34 corpus occurrences are followed by རྗེ/རྗེའི/རྗེས. A bare རྡོ stays `do`.
   - `ཤོག` → `scho` in both conventions. Evidence: Chakrasamvara 8:1, Gebetsbuch 5:0; the Hayagriva
     booklet itself mixes both.
   - `ཅི` → `tschi` (the rule output). The earlier `dschi` rested on a 2:1 observation, and the
     Gebetsbuch prints `tschi` (2×).
   - `ལྷན` → `lhän` (the rule output). The `län` evidence is weak (2 observations), and the l/I
     font ambiguity is documented.
2. **Genitive umlaut after o/u** differs by convention:
   - `tz-aktuell`: keep it (`tschen pö`, Hayagriva booklet p. 7).
   - `tz-gebetsbuch`: no umlaut (`tschu`, `gya tso`). Held-out evidence: 4 tokens. Mark this as
     low-evidence in a code comment.
   - `pa'i` → `pä` stays in both conventions.
3. **Mantra letter table calibration.**
   - Extract the all-caps mantra lines from the existing local OCR of the three TZ PDFs
     (`data/derived/phonetics-research/ocr/`). If that directory is missing, re-run Tesseract
     locally (`deu`, 300 dpi). Read **only** the extracted caps lines, not whole pages.
   - Align the letter conventions with TZ practice: the Hayagriva booklet p. 7 prints
     `SOBHAVA SHUDDHA SARVA DHARMA … SHUDDHO HANG`, i.e. `SH` and `V`, not `SCH` and `W`.
   - Record which choices the TZ lines support and which remain guesses.
   - Keep the curated Tibetan-pronunciation lexicon (`BENDSA`, `PEMA`, `SOHA`, `PHE`, `HUNG`, …).
   - The conventions differ for mantras only where the TZ evidence says so. Otherwise mantras are
     identical in both.
4. **Convention rewrite, complete list.** `tz-gebetsbuch` differs from `tz-aktuell` only by:
   - onset `th→t`, `tsh→ts`, `kh→k` (including `khy→ky`), `thr→tr`, `ph→p`, `dz→ds`;
   - item 2.

   Everything else is identical: `tsch`, `dsch`, `sch`, `g/d/b`, umlauts, `scho`. Encode the
   rewrite as data and cover each rule with a test.
5. Keep the per-syllable `origin` in the generator's result objects. It is **not** written into
   `publication.json` (§5).

## 5. PRM contract change (v2.0 → v2.1)

The change is additive at the publication level. The pronunciation shape is replaced. Update
`read-model.ts`, projector validation, README and tests together. Do not add a compatibility shim.

```ts
// publication level, data-driven like translation_layers
pronunciation_conventions: {
  id: string            // 'tz-aktuell' | 'tz-gebetsbuch'
  label: string         // D5
  description: string   // one sentence, German, for the help text
  default: boolean      // exactly one true
}[]

// passage level
pronunciation?: {
  id: string                                   // pronunciation:de:<passage-id>
  language: 'de'
  status: 'generated'
  generator: { name: 'atp.phonetics.tz'; version: string }
  source_block_id: string
  variants: {
    convention_id: string
    lines: { tibetan: string; pronunciation: string }[]
  }[]
}
```

Invariants, enforced by the projector (fail loudly):

- Every passage with non-empty Tibetan source gets a pronunciation. Every pronunciation has exactly
  one variant per declared convention.
- For each variant, the `tibetan` slices concatenate **byte-exactly** to the source block text,
  including ༄༅, shad, spaces and newlines. Lines are split at phrase boundaries (shad / gter
  tsheg). Physical newlines are not phrase breaks.
- `pronunciation` is outside the translation layers (existing rule). No ID collides with a layer
  or target ID.
- The output is byte-deterministic for identical inputs.
- The note text shown in the Reader derives from the data. Proposal: "Aussprachehilfe ·
  automatisch erzeugt · <label>".

Check the bundle-size delta after the build and report it (both variants of about 12k syllables).

## 6. Reader UI

- Keep the existing `Aussprache` toggle and its coupling to `Tibetisch`.
- While `Aussprache` is on, show a compact convention selector in the same control group. Use a
  segmented control or a radiogroup with correct ARIA, labels from `pronunciation_conventions`,
  and no hard-coded convention IDs in React.
- Switching the convention uses the existing `preserveViewport` path. There must be no scroll jump.
- Persist the choice in `localStorage` under a release-independent key. Wrap reads and writes in
  `try/catch` and fall back to the `default` convention.
- The help text on hover/focus uses the task-facing style of the current Reader polish, for
  example: "Zwei TZ-Schreibweisen: aktuell mit markierter Behauchung (tshog), Gebetsbuch ohne (tsog)."
- Mantra lines render as they come; no special styling is required.
- Remove the "Für diese Passage liegt noch keine Aussprachehilfe vor." path only if every passage
  now has an aid. Otherwise keep it.
- Check desktop plus 390/320 px. The selector must not overflow the sticky controls.

## 7. Tests and acceptance

1. **Unit tests** in `tests/unit/test_phonetics_tz.py` or a comparable location, all offline:
   - syllable parsing cases (prefix/superscript/root/subscript/suffix/post-suffix, fused particles
     འི འོ འུ འང འམ, missing-tsheg split);
   - every item in §4;
   - each convention rewrite rule;
   - Sanskrit detection and casing.
2. **Held-out regression.** Move `gebetsbuch_heldout.tsv` next to the tests. The `tz-gebetsbuch`
   convention must keep ≥ 97.0 % identical TZ tokens (currently 551/566). Report the new figure;
   §4.2 should raise it. The header must keep stating that the Tibetan side is assistant-
   reconstructed and unverified.
3. **Projector tests** (`test_converter.py`): update them for the v2.1 shape and the invariants in
   §5, including a mutated-input test for slice concatenation. Remove the six-example assertions.
4. **Existing gates** must stay green: `npm test`, `npm run build` (the pre-existing large-chunk
   warning is acceptable), Reader Chromium smoke (`browser-smoke.cjs`), Workbench smoke.
   - Extend the Reader smoke: turn on Aussprache, switch the convention, check that a known
     passage changes (e.g. `tshog` → `tsog`), reload and check persistence, and check that there is
     no page error or external request.
5. Visually inspect screenshots at desktop and 390/320 px. Store the evidence under
   `data/derived/hayagriva-reader-pronunciation/`.

## 8. STOP rules

Stop and report instead of guessing in these cases:

- The byte-exact slice invariant cannot be met for some passage structure.
- The mantra calibration evidence contradicts §4.3 in a way that needs an owner decision.
- D5 is still open when you reach §6.
- The held-out score drops below 97.0 %.
- Any change would touch the Workbench authoring contract or store.

## 9. Documentation (AGENTS.md §1, §7)

- Update the README (contract section, launch/test commands).
- Add a follow-up section to `docs/research/phonetics-01-tz-generator-exploration.md` with the new
  held-out figure and the mantra calibration findings.
- Add an engineering-log entry with an offset-aware timestamp. Add a CHANGELOG entry.
- Update `docs/research/phonetics-01-erklaerung-methodik-und-stand.md` §4/§5 (built / not built).

The end report lists:
- what was inspected, what changed and what was measured;
- the bundle-size delta and the artifact paths;
- the remaining uncertainty: mantras; the Tibetan side of the held-out test being unverified;
  TZ's own inconsistency;
- the commit hash, only if the owner has asked for a commit.


---

## 10. Revisions during execution (2026-09-25T19:01:52+02:00)

The owner changed several decisions while the prompt was being executed. These revisions take
precedence over §§1, 4 and 5 above. The implementation follows them.

- **D2 replaced: no mantra treatment.** There is no mantra detection, no capitals and no mantra
  lexicon mode. Every syllable is read on its own; units written with Sanskrit letters or marks are
  read letter by letter. The §4.3 plan to calibrate a Sanskrit spelling style was dropped after the
  owner stated that the transcription must render the Tibetan characters actually written, as they
  are pronounced.
- **D5 extended to three variants.** The generator got independent switches (`atp.phonetics.tz.Options`):
  - aspiration marking;
  - `dz`/`ds`;
  - genitive umlaut after o/u;
  - connected speech (རྡོ་རྗེ *dor*);
  - TZ spellings (ཤོག *scho*);
  - Sanskrit traditional readings or letters;
  - anusvara after u as *ng* or *m*;
  - Sanskrit-syllable capitals.

  The Reader offers three pre-generated variants: `tz-aktuell` (default), `tz-gebetsbuch`
  (aspiration unmarked, *ds*, no genitive umlaut after o/u) and `silbengetreu` (no connected
  speech, *schog*, Sanskrit read from the letters: *badzra, padma*). All three use *hung*.
- **PRM names.** The publication field is `pronunciation_variants`, and the passage variants use
  `variant_id` (instead of `pronunciation_conventions` / `convention_id`).
- **§4.1 executed as switches.** *dor* and *scho* are now switches. ཅི stays *tschi* and ལྷན stays
  *lhän*.
- **Result.** Held-out Gebetsbuch test: 98.4 % (`tz-gebetsbuch`). All gates are green. See the
  engineering log entry of 2026-09-25T19:01:52+02:00.
