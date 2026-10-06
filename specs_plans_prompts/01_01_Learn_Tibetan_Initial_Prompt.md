# Repository Agent Brief — Learn Tibetan

## Mission

Build a polished, mobile-first web app for learning to **read Tibetan Uchen script**, with a fast, Duolingo-like multiple-choice interaction model.

The primary user already has some familiarity with Devanagari and wants to learn Tibetan script efficiently by understanding its **traditional phonetic grouping**, not by memorizing 30 unrelated symbols.

The app should begin with the alphabet and vowels, then introduce pronunciation/audio as its own learning chapter, and later scale naturally to Tibetan syllables and simple words.

Do **not** overengineer the first version. The core experience should be extremely fast, clear, attractive, and usable one-handed on a phone.

Before substantial implementation, inspect the repository and the supplied reference material, then write a short implementation plan. Make sensible technical decisions yourself unless they would materially change the product described here.

---

## Repository reference material

A supplied transliteration/pronunciation package will be placed at:

`references/transliteration/`

Read this material before designing Tibetan text handling, especially:

- `README_UMSCHRIFT.md`
- `src/atp/phonetics/tz.py`
- `src/atp/phonetics/wylie.py`
- `tests/unit/test_phonetics_tz.py`
- `tests/unit/test_phonetics_wylie.py`
- `docs/tz-umschrift.md`
- `integration_example/`

Treat the supplied Python implementation and tests as the initial reference implementation for:

1. Tibetan → Wylie/EWTS transliteration
2. Tibetan → German-readable pronunciation in the style used by the Tibetisches Zentrum ("TZ")

Do **not** independently reinvent these rules.

Preserve the conceptual separation between:

- Tibetan orthography
- Wylie/EWTS transliteration
- learner-facing TZ pronunciation
- audio pronunciation

These are different representations and must remain separate in the data model.

The transfer package is internal reference material. Do not assume it can be republished unchanged; retain any provenance/license notes and avoid exposing it as a public third-party package without checking rights.

---

## Product philosophy

The app is primarily a **recognition trainer**, not a textbook.

The basic loop should feel like:

> see prompt → tap one of four answers → immediate feedback → next prompt

No unnecessary "Continue" button after every answer.

A session should be easy to use for 30 seconds or 20 minutes.

The app must feel good on a phone:

- large thumb-friendly answer targets
- very large Tibetan glyphs
- minimal UI clutter
- fast transitions
- no tiny controls
- no desktop-first layout squeezed onto mobile
- immediate visual feedback
- optional subtle haptic feedback where supported

The Tibetan script is the visual focus.

---

## Recommended technical baseline

Prefer:

- React
- TypeScript
- Vite
- Progressive Web App (PWA)
- client-side persistence
- static deployment

No backend, login, cloud database, or server API is required for the initial app.

The app should work offline after installation/first successful load.

Keep dependencies modest. Do not introduce a heavy component framework merely to obtain basic buttons and cards.

Choose a suitable open-source Tibetan font with good Uchen rendering and make offline behavior reliable. Document the font/license decision.

The agent may refine this stack if there is a concrete technical reason, but should explain the reason before changing it.

---

# Curriculum

## Chapter 1 — The Tibetan alphabet as a system

Do not present the alphabet as 30 arbitrary symbols.

Teach and display it in its **traditional order and grouping**.

The first four rows are especially important because they correspond closely to the Indic/Devanagari organization:

| Tibetan | Traditional/phonetic grouping | Devanagari parallel |
|---|---|---|
| ཀ ཁ ག ང | velar / traditional "guttural", back of mouth | क ख ग ङ |
| ཅ ཆ ཇ ཉ | palatal series / historically Indic palatal row | च छ ज ञ |
| ཏ ཐ ད ན | dental/alveolar series | त थ द न |
| པ ཕ བ མ | labial series | प फ ब म |

Continue with the remaining Tibetan letters in traditional alphabet order.

The UI may use beginner-friendly German labels such as:

- Kehllaute / Hintergaumen
- Gaumenlaute
- Zahn-/Zahndammlaute
- Lippenlaute

Where useful, also expose the more technical linguistic label in secondary text.

Do not force modern phonetics into a misleadingly simple historical classification. A short note can explain that these rows come from the Indic articulatory system and that modern Tibetan pronunciation is not identical to Classical Sanskrit pronunciation.

### Devanagari support

Because the primary learner already reads some Devanagari, make Devanagari correspondence an **optional learning aid** on alphabet/reference cards.

Example:

- Tibetan: ཀ
- Wylie: `ka`
- Devanagari parallel: `क`
- group: velar

Do not show Devanagari by default inside every quiz answer, because it could become a crutch and prevent direct Tibetan recognition.

A simple "Show Devanagari parallels" preference is sufficient.

---

## Chapter 2 — Tibetan glyph → Wylie

This is the first rapid drill.

Example:

Prompt:

`ཅ`

Answers:

- `ca`
- `cha`
- `ja`
- `nya`

The correct answer is canonical Wylie/EWTS, not an English-style pseudo-phonetic spelling.

Important distinction:

- ཅ → Wylie `ca`
- learner-facing German/TZ pronunciation may be approximately `tscha`

Do not conflate those.

Use four large answer buttons.

After a correct answer, proceed automatically after a very short feedback delay.

After a wrong answer:

- clearly show the correct answer
- avoid punishment/game-over behavior
- reintroduce that item relatively soon

---

## Chapter 3 — Wylie → Tibetan glyph

Reverse the mapping.

Example:

Prompt:

`ca`

Answers:

- ཅ
- ཆ
- ཇ
- ཉ

Again, four large thumb-friendly choices.

The user should eventually develop direct bidirectional recognition:

`ཅ ↔ ca`

---

## Chapter 4 — Vowels

After the consonants are sufficiently familiar, introduce the five basic vowel readings:

- inherent `a`
- `i`
- `u`
- `e`
- `o`

Teach them first on a simple base consonant, then generalize.

For example:

- ཀ — ka
- ཀི — ki
- ཀུ — ku
- ཀེ — ke
- ཀོ — ko

Support the same two written drill directions:

- Tibetan → Wylie
- Wylie → Tibetan

The content model must allow the transliteration/pronunciation reference tools to generate or verify these forms rather than manually duplicating rules throughout the UI.

---

## Chapter 5 — Audio recognition

Audio is a **first-class curriculum chapter**, not a vague optional future feature.

The task is:

> hear Tibetan → choose the correct Tibetan glyph or syllable

The first audio exercises should use the same alphabet/vowel material already learned visually.

Examples:

- play pronunciation → choose ཀ / ཁ / ག / ང
- play pronunciation → choose ཀི / ཀུ / ཀེ / ཀོ

### Important audio architecture rule

Do not make the runtime app depend on a cloud Text-to-Speech service.

Prefer **bundled static audio assets** so playback is:

- instant
- offline
- reproducible
- replaceable
- cheap

Create a clean audio abstraction in the app so any item can reference a curated audio file.

For generating candidate recordings during development, investigate a local Tibetan TTS pipeline. A known candidate is Meta's Central Tibetan MMS/VITS model (`facebook/mms-tts-bod`), but verify current availability, licensing, quality, and suitability before depending on it.

Treat generated audio as a **candidate source**, not unquestionable truth.

Single Tibetan letters may not be synthesized reliably by a model trained primarily on normal speech. Therefore:

- generated clips must be easy to inspect
- any clip must be replaceable by a manually recorded/curated version
- the content data should store source/provenance for audio when practical
- target dialect/reading should be documented

Do not implement speech recognition or pronunciation scoring in the initial app. That is a different problem from audio playback and can be considered later.

---

## Chapter 6 — Tibetan syllable structure

Design the data model and UI architecture so the app can later progress from letters into real Tibetan syllables.

The supplied transliteration package already contains useful parsing/analysis logic. Reuse or adapt it rather than inventing another Tibetan parser.

A later exercise/reference view should be able to explain a syllable such as:

`བསྒྲུབས`

in terms of positions such as:

- prefix
- superscript
- root/base letter
- subscript
- vowel
- suffix
- second suffix

and show parallel representations such as:

- Tibetan
- Wylie
- TZ pronunciation

Do not make this advanced material block the initial alphabet experience, but do not design the early data model in a way that makes it impossible.

---

## Chapter 7 — Simple words

Once syllable structure is available, add simple common Tibetan words.

The important pedagogical contrast will often be:

- what is written
- what Wylie encodes
- what is actually pronounced

This is precisely why Wylie and TZ pronunciation must remain separate fields.

---

# Transliteration and pronunciation data model

Create a content model capable of representing at least:

```ts
{
  id: string;
  tibetan: string;
  wylie: string;
  tzPronunciation?: string;

  order?: number;

  group?: {
    id: string;
    labelDe: string;
    linguisticLabel?: string;
  };

  devanagariParallel?: string;

  audio?: {
    src: string;
    source?: string;
    dialect?: string;
  };

  tags?: string[];
}
```

This is illustrative, not mandatory API design.

The key architectural rule is that these fields stay conceptually separate.

Where possible, Wylie/TZ forms for larger Tibetan content should be generated or validated using the supplied reference engine rather than manually maintained.

The React runtime should not require a Python interpreter.

A good architecture is likely:

Tibetan curriculum source data  
→ build/development generation/validation step using Python reference tools  
→ static JSON/TypeScript content consumed by React

The agent may choose another clean approach, but avoid shipping Python into the browser merely to transliterate a fixed beginner curriculum.

Preserve tests around the imported/adapted transliteration logic.

---

# Quiz behavior

Keep the first implementation deliberately simple but adaptive.

Requirements:

- introduce letters in small groups
- keep the traditional alphabet order visible
- review previously learned items cumulatively
- wrong answers should recur soon
- consistently correct items should recur less frequently
- avoid purely uniform random sampling

Do not build a huge spaced-repetition framework unless there is a concrete need.

### Distractors

Distractors should be pedagogically useful.

Prefer, in roughly this order:

1. members of the same traditional row/group
2. visually similar glyphs
3. transliterations/pronunciations that are easy to confuse
4. other already-learned items

Avoid three absurdly unrelated answers that make the question trivial.

Keep distractor generation deterministic/testable enough to avoid accidental duplicate answers or ambiguous questions.

### Ambiguity

Some different Tibetan letters may share the same learner-facing TZ pronunciation.

Therefore **do not create quiz questions whose answer is inherently ambiguous**.

For example, if two letters collapse to the same TZ learner pronunciation, a "TZ pronunciation → choose one letter" question may be invalid unless additional context distinguishes them.

The quiz engine should be able to detect/exclude ambiguous prompts.

Audio exercises need the same caution.

---

# Progress and sessions

Store progress locally.

A simple first model is enough:

- seen count
- correct count
- recent mistakes
- familiarity/mastery score
- unlocked chapter/group

Do not require an account.

Provide a quick way to:

- start/continue learning
- practice all learned material
- review difficult items
- reset progress

Do not turn the app into a gamification circus.

A small progress indication is good. Streaks, currencies, leagues, avatars, social systems, etc. are out of scope.

---

# Visual direction

The supplied visual reference shows a useful basic pattern:

- large Tibetan glyphs
- clear grid
- minimal clutter
- strong contrast
- direct access to quiz mode

Keep that simplicity but make the result feel modern and deliberate rather than like an old Android utility.

## Palette

Base the visual identity loosely on Tibetan monastic robes and Gelug visual culture:

- deep chestnut / robe red
- rich saffron / ochre / deep yellow
- warm cream / eggshell
- dark brown
- very restrained plum/purple accents

Approximate starting palette, refine as needed:

- robe red: `#6F2634`
- saffron/ochre: `#D39A28`
- darker mustard gold: `#B77A20`
- warm cream: `#F4EBDD`
- dark brown: `#30231F`
- restrained plum: `#6C496C`

Do not use all colors everywhere.

Preferred hierarchy:

- cream/light warm surfaces
- robe red as strong structural/accent color
- gold/ochre for progress, highlights, and selected states
- dark brown for text
- plum only as a tiny accent

Avoid generic bright Material Design blue/green styling.

## Typography

Tibetan glyphs should be large, beautiful, and correctly rendered.

On a phone, a single-letter quiz glyph can easily occupy roughly 100–140 CSS px depending on the chosen font and viewport.

The Latin/German UI should remain restrained and readable.

---

# Main screens

Keep navigation small.

A reasonable initial structure:

## Home

- continue learning
- current chapter/group
- practice
- alphabet/reference

## Learn / Quiz

- progress indicator
- prompt
- four answers
- instant feedback
- no unnecessary modal dialogs

## Alphabet / Reference

Show the traditional alphabet in grouped rows.

Each item can expose:

- Tibetan glyph
- Wylie
- optional TZ pronunciation
- optional Devanagari parallel
- group/articulation information
- audio button when audio exists

This view should preserve the structural clarity of the supplied screenshot/reference rather than becoming a dense dictionary table.

## Settings

Only useful settings, for example:

- show/hide Devanagari parallels
- show/hide TZ pronunciation in reference views
- audio volume / auto-play where appropriate
- reset learning progress

Keep settings boring and small.

---

# UX details

Prioritize:

- portrait phone usage
- one-thumb interaction
- no accidental double submits
- keyboard accessibility on desktop
- proper focus states
- reduced-motion preference
- semantic buttons
- accessible contrast
- fast first render
- offline support

Correct answer feedback should be satisfying but brief.

Wrong answer feedback should be informative, not punitive.

Avoid long animations that slow repetition.

---

# Testing

Add tests where they buy real confidence, especially for:

- curriculum ordering
- Tibetan/Wylie mappings
- imported/adapted transliteration behavior
- ambiguous-question exclusion
- distractor uniqueness
- progress/mastery updates
- persistence
- PWA/offline-critical behavior where practical

Preserve the reference transliteration tests when extracting/adapting that code.

Do not chase meaningless coverage percentages.

---

# Out of scope for the initial app

Do not add these unless needed by the architecture or explicitly requested later:

- user accounts
- backend/API
- cloud database
- social features
- leaderboards
- subscriptions/payments
- chat tutor
- generative AI inside the runtime app
- handwriting recognition
- Tibetan keyboard input exercises
- speech-to-text
- pronunciation scoring
- large dictionary
- grammar course
- complex spaced repetition engine

The architecture may leave room for them, but do not build them now.

---

# Working style for this repository

1. Inspect the existing repo first.
2. Inspect `references/transliteration/` carefully.
3. If a UI reference image is present under `references/ui/`, inspect it.
4. Write a concise implementation plan before large code changes.
5. State any assumptions that materially affect pedagogy or architecture.
6. Implement in coherent increments.
7. Keep the app runnable throughout development.
8. Do not silently replace Wylie with phonetic spelling.
9. Do not silently invent Tibetan pronunciation rules already covered by the reference package.
10. Prefer simple, inspectable data and logic over clever abstractions.
11. When uncertain about Tibetan linguistic content, isolate the uncertainty in data/configuration rather than baking guesses into application logic.
12. At the end, document:
   - how to run the app
   - how to run tests
   - how curriculum content is represented
   - how transliteration/TZ generation is performed
   - how to add/replace audio files
   - how to build/install the PWA

---

# First task

Start by:

1. inspecting the repository and reference package;
2. proposing the concrete application architecture and file structure;
3. identifying any existing project setup that should be preserved;
4. defining the initial curriculum data shape;
5. explaining how the supplied Python transliteration/TZ code will be integrated without creating a runtime Python dependency;
6. then implement the app.

Do not spend a large amount of time on speculative future architecture before the alphabet learning loop works beautifully.

The first experience to optimize is simple:

**Tibetan glyph → recognize it immediately → tap the correct Wylie answer → next.**

Everything else grows from that.
