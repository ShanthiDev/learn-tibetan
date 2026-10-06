# Hayagrīva Reader

**Created:** 2026-09-23T00:23:20+02:00
**Last updated:** 2026-09-27T16:58:29+02:00
**Status:** current
**Origin:** repository_agent_generated
**Document role:** reference_resource_note

A static, publication-first React Reader and local candidate-authoring Workbench for the complete
current Hayagrīva working corpus. It has no backend, accounts, canonical ATP migration or publication
write machinery. Translation, diplomatic and interpretation content is working data; human
publication approval is not established. Read mode remains the clean default.

The deliberately narrow architecture is:

```text
v10/question-curated ATP-lite bundle
    ├→ disposable deterministic projector → Publication Read Model v2.3 → React Reader
    └→ exact authoring bases ──────────────→ Authoring Context v3 ──────→ local Workbench
tracked post-v10 authoring store + rule/evidence registries
    ├→ explicit editions (every passage pinned) ↗
    └→ explicit public projection ↗
```

The React application imports only the generated read/authoring views and has no knowledge of ZIP
members, ATP-lite paths, canonical ATP classes or repository store layout.

On first access, and again 24 hours after the most recent confirmation, a modal notice requires the
reader to confirm that they are entitled to read the initiation-restricted practice text. The
browser stores only the confirmation timestamp in `localStorage`; clearing site data or denying
storage causes the notice to return. A persistent **Nur mit Initiation** label remains in the
upper-right masthead. This is an explicit practice-access acknowledgement in the static Reader,
not server-side authentication or an authorization boundary.

## Candidate authoring

Choose **Bearbeiten** to self-declare an author identity, edit the complete German recitation body
of a unit and save it as a new immutable proposal. Block order/kinds and mantra metadata are retained.
The baseline and every parent survive; sibling revisions are legitimate branches. The Workbench
shows the selected version in the normal passage position together with symmetric baseline/candidate
metadata, parentage, direct rationale and a deterministic line diff. It can also preserve a minimal
unresolved human observation without coercing it into a wording change or Issue resolution.

**Meine Änderungen** provides a read-only cross-text check before export. Opening it always brings
the review list below the fixed controls into view. **Im Text ansehen** keeps that list open, selects
the candidate and explicitly navigates on every activation, including repeated visits to the same
passage. The panel's **Schließen** action hides the list explicitly; its toolbar action opens it
again without discarding the review state. An author can mark their own local proposal as withdrawn
without deleting or mutating it. The optional reason appears only after the author chooses
**Version verwerfen**; saving still needs the final browser confirmation. Withdrawn proposals are
hidden from ordinary choices but remain available in explicit history and as required ancestors of
active descendants. Read mode shows the wording of the selected reading version (see below).

Candidates, Activities, Agents, ReviewNotes, withdrawal records and unfinished drafts use
release-namespaced IndexedDB.
Saved objects survive reload; local proposals never change a reading version. A structured file can
be downloaded and re-imported into a fresh browser. Import validates exact release/base/body hashes,
block structure, provenance, dependency closure, cycles and immutable ID reuse before one atomic
workspace update. v1/v2 workspaces and packages migrate deterministically to v3; the only change to
saved candidates is dropping the person field that duplicated their Activity. Storage failure is shown explicitly. Cross-tab live sync and advanced quota
recovery remain outside Phase 2.

All layout-changing Reader controls preserve the current semantic passage and viewport offset,
including translation layer, Tibetan, pronunciation, meaning, annotations, Questions, Workbench
mode and candidate selection. This behavior is measured at desktop, 390 px and 320 px widths.

Returned files are validated and ingested with the standard-library Python CLI into
`data/authoring/hayagriva/store.json`; intake itself does not expose or publish them. Full commands,
hash semantics, privacy boundary and limitations: [`../../docs/authoring.md`](../../docs/authoring.md).

## Run locally

Required local source:

```text
data/reference_hayagriva_atp_lite/hayagriva_atp_lite_bundle_rez_v10_question_curated.zip
```

Its SHA-256 is `24230b7d3ab9047364176182b0d67ca49ba0d06f83927f6d24654087a37146d7`.
The older v09/Paket-F and v07/Paket-D bundles are superseded inputs and are not read by the
projector. From the repository root (Node 24, npm, Python 3.11+):

```bash
cd web/hayagriva-reader
npm ci
npm run dev
```

Open http://localhost:5173. Dev and build regenerate `src/generated/publication.json` from v10.

```bash
npm test
npm run build
npm run preview
node scripts/browser-smoke.cjs
npm run test:browser-authoring
```

Production preview: http://localhost:4173. Deep-link example:
http://localhost:5173/#r04-u06. Fragment IDs identify passages, not UI preferences. Fonts are
bundled locally; the redistributed license is `public/FONT-LICENSE.txt`.

## Current measured projection

- 19 ordered sections and 192 passages;
- all 258 diplomatic segments, assigned exactly once through explicit `derived_from` IDs;
- all six recitation block kinds, 515 diplomatic notes, 61 diplomatic alternatives and 165 sense
  sketches;
- 201 logical curated Questions on 119 recitation passages and 58 separate atomic Issues on 37
  diplomatic passages;
- exactly 58 explicit Question–Issue relationships; every linked Question is one object with both
  recitation and diplomatic targets, never a duplicated Question;
- no active `sense.offen` family;
- a generated German pronunciation aid for all 192 passages in three variants (TZ aktuell, TZ
  Gebetsbuch, Silbengetreu), outside translation layers and labelled `generated`;
- 40 exact House Decision references as the only structured external-reference kind.

## Reading versions (editions)

The **Textstand** control lists every reading version. The one marked **(aktuell)** is the store's
explicit `current_edition_id` and opens by default; v10 stays selectable. A version is chosen
explicitly, never "the newest". `?edition=<id>` links to another version. **Versionsgeschichte**
shows, per version, its selection rule, the adopted rules with their scope, and the changed
passages. When a passage shows post-v10 wording, meaning, annotations and curated Questions are
labelled as referring to the v10 wording. Post-v10 reviewer requests (Questions addressed to a
named role, with explicit answer options) appear in the **Fragen** view of the versions whose
wording they quote. In Workbench mode the version shown by the selected reading version is the
preselected base for further edits; rule-application versions show roles, rules, evidence with
verification status and the hits of the passage. Contract and intake: `docs/authoring.md`.

## Publication Read Model v2.3

Contract: [`src/read-model.ts`](src/read-model.ts).
Generated data: `src/generated/publication.json` (ignored and rebuilt).
Projector: [`scripts/convert_sample.py`](scripts/convert_sample.py), Python standard library only.

PRM v2.0 was a breaking replacement for v1.2; v2.1 adds generated pronunciation variants and
replaces the former six hand-written pronunciation examples; v2.2 adds a generated Wylie (EWTS)
transliteration per passage; v2.3 replaces the single `edition` by `editions[]` plus
`default_edition_id`, lets several recitation translations of a passage coexist (each listing the
`edition_ids` that show it) and adds `reviewer_request` Questions. There is no runtime legacy adapter.
The main shape is:

```text
Publication
  release
  editions[{id, label, status, translation_layer_ids, note, recorded_at?, history?}]
  default_edition_id
  pronunciation_variants[{id, label, description, default}]
  translation_layers[]
  attributions[]
  references[]
  targets[]
  annotations[]
  questions[]
  issues[]
  sections[].passages[]
    source.blocks[]
    translations[{layer_id, edition_ids[], candidate_id?, blocks[]}]
    meaning?
    pronunciation?{status: generated, generator{name, version}, source_block_id,
                   variants[{variant_id, lines[{tibetan, pronunciation}]}]}
    transliteration?{scheme: ewts, status: generated, generator, source_block_id,
                     lines[{tibetan, text}]}
```

**Pronunciation.** `pronunciation` is produced at build time by `atp.phonetics.tz`
(`src/atp/phonetics/tz.py` at the repository root), one variant per entry of
`pronunciation_variants`; exactly one variant is the default (`tz-aktuell`). The projector
enforces that every passage with Tibetan source has a pronunciation, that each declared variant is
present exactly once, and that each variant's `tibetan` slices concatenate byte-exactly to the
source block. Lines end at Tibetan phrase marks (shad), not at physical newlines. The Reader shows
a "Schreibweise" selector while "Aussprache" is on and remembers the choice in `localStorage`
(`hayagriva:pronunciation-variant`). `transliteration` (`atp.phonetics.wylie`) uses exactly the
same line slices as the pronunciation variants, so the Reader's separate "Wylie" control can show
it alone or together with the pronunciation, line by line. How the generator works and why it can
be trusted:
[`docs/tz-umschrift.md`](../../docs/tz-umschrift.md).

The contract keeps four dimensions separate:

- `language`: BCP-47-like language tag on source, edition, pronunciation and translation layers;
- `mode`: scholarly translation role such as `recitation` or `diplomatic`;
- `style_policy`: optional bounded display metadata, not canonical `CurationPolicy`;
- `edition`: a coherent reading version that selects exactly one translation per passage and layer,
  not another mode or style label.

Passages therefore contain a generic `translations[]` collection keyed by layer ID. The Reader
derives controls and lookup from `translation_layers[]`; adding a synthetic English/readable layer
requires no new passage field or rendering branch. No fake English corpus content ships in the
fixture.

## Identity and target policy

Upstream IDs are preserved wherever available: passage fragments such as `r04-u06`, recitation
mark-based annotation/Question IDs, `issue:*` IDs and `HD-*` references. Layer IDs use stable
semantic coordinates such as `translation:de:recitation`, independent of display labels.

Source blocks use stable passage identity. Legacy translation blocks, diplomatic notes and
alternatives without upstream IDs use:

```text
stable parent ID + object kind + SHA-256 digest of canonical meaningful content
```

If identical siblings occur under one parent, an occurrence number among identical siblings is
added; array position alone is never the identity. Different payloads colliding on a digest fail.
All IDs and bytes are deterministic for identical inputs. A synthesized legacy ID is stable within
this publication release and across identical rebuilds; without an upstream revision map it is not
claimed to survive an arbitrary scholarly rewrite.

Reusable targets identify passage, Tibetan source, translation layer, block and—where uniquely
validated—an exact span. Span offsets count Unicode code points, not UTF-8 bytes or JavaScript
UTF-16 units; the projector validates `block_text[start:end] == quote`. Ambiguous/repeated legacy
anchors fall back to the narrowest proven layer target. Diplomatic free-text `scope` is not promoted
to an exact selector. Every Question identifies its primary target separately from additional
discovery targets. If the active layer has only a block/layer target, the Reader retains the exact
quote from that primary target instead of making the cited locus disappear. React DOM order and
current display state never define a target.

## Questions, Issues and provenance

Questions are the curated reviewer-facing requests; Issues are separate actionable status objects.
The projector uses only explicit v10 Question marks. It never infers Questions from `sense`,
`sense.offen`, punctuation or Issue-like prose, and fails if active `sense.offen` reappears.

The 58 explicit `issue:*` references create reciprocal Question–Issue relationships. Each linked
Question reuses diplomatic Issue targets in addition to its recitation target, so it is discoverable
in both Reader contexts while retaining one logical ID and count. Issue workflow status remains a
queryable field separate from source/content status.

The attribution projection is intentionally bounded:

- the v09 evidence shows all 106 earlier Question marks and all 139 former `sense.offen` concerns
  under `claude-fable-5-1` recitation runs;
- mapping-ledger actions identify 130 current Question wordings and 29 split Issue wordings as the
  result of the latest curation; the owner identifies its author as GPT-5.6 Sol with `high`
  reasoning effort;
- Andreas is separately recorded, by owner statement, as the person who entered/submitted the
  curated Questions and Issues;
- unchanged current wording retains its earlier model attribution; reworked wording points to the
  earlier model attribution through `derived_from_attribution_ids`;
- no human substantive authorship beyond that owner-supplied recorder role is inferred.

This is Reader-facing provenance, not a full activity graph. Translation and annotation records
carry the explicitly recorded source-run model plus machine/source status. Unknown attribution is
allowed.

## References and Reader behavior

Only exact `HD-*` IDs already present and resolvable in `house_decisions.jsonl` become structured
House Decision previews. `SJ-*`, `tz:*`, `issue:*`, literature abbreviations and free text stay
unlinked. An `issue:*` reference is a Question–Issue relation, not an external-reference preview.

The clean default remains reading-first. Hover or keyboard focus on the normal layer controls shows
concise help for the respective purpose of the recitation and diplomatic translations; editing and
explanatory controls describe their action in the same way without separate info buttons. Generic
controls reveal exact Tibetan, the generated pronunciation aid in a selectable variant,
sense sketches and layer-specific annotations. The global **Fragen** control filters by logical
Question identity in the current layer, retains passage context and supplies previous/next
navigation. Passage-level question controls stay deliberately small and muted. In diplomatic
context the related Issue statement and its explicit status remain distinct from the Question
behind a labelled, collapsed “Zugehöriges Issue” disclosure; it no longer reads like a second
Question by default. Layer changes preserve the current passage position; passage fragments remain
stable.

The floating contents panel, responsive 390/320 px layout, locally bundled Tibetan font,
copy/paste behavior and reduced-motion wordmark behavior remain unchanged. No external network
request is expected.

## Verification

`npm test` runs 25 focused Python checks and the TypeScript contract suite, covering the exact bundle hash, generalized
additional-language layer, namespace uniqueness, referential integrity, byte determinism, stable
deep links, selector semantics, legacy-ID collision handling, all corpus counts, 201/58 logical
Question/Issue normalization, multi-target discovery, `sense.offen` rejection, attribution/status,
House Decision STOP rules, generated pronunciation variants and their invariants, all 192 exact authoring bases, shared Unicode
hash vectors, immutable/idempotent intake, branching, ReviewNotes, block preservation and public
allowlisted exposure.

`npm run build` regenerates the projection, type-checks and builds production assets. The optional
`scripts/browser-smoke.cjs` uses the declared `playwright-core` test dependency and a locally installed
Chromium against port 4173 and
checks desktop plus 390/320 px layouts, full rendering, data-driven layer switches, exact Tibetan
clipboard roundtrip, logical questions and distinct Issues, scroll stability, references, deep
links, pronunciation variants (switching, viewport stability, persistence, mobile overflow), page
errors and external requests. Current artifacts are written to
`data/derived/hayagriva-reader-phase1/`; pronunciation screenshots to
`data/derived/hayagriva-reader-pronunciation/`.

`npm run test:browser-authoring` covers immutable edit/save/diff, ReviewNote capture, reload,
portable export/import in a fresh browser, duplicate import, tampered-base rejection, visible
storage denial and 390 px layout. Artifacts go to `data/derived/hayagriva-workbench-phase2/`.
Browser checks require `npm run preview` in another process.

Phase 2 stops before answers/Issue resolution, publication selection, backend services, canonical
ATP migration, source editing, general annotations and audio tooling.
