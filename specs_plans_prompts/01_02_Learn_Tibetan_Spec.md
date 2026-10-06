# 01_02 — Learn Tibetan: Spezifikation (MVP, Kapitel 1–5)

**Stand:** 2026-10-06 · **Basis:** `01_01_Learn_Tibetan_Initial_Prompt.md` (bleibt die
Produktvision; diese Spec konkretisiert sie und hält Abweichungen fest) · **Regeln:** `AGENTS.md`

## 1. Ziel und Umfang

Mobile-first PWA zum **Lesenlernen der tibetischen Uchen-Schrift**, Duolingo-artiger
4-Antworten-Drill. Kernerlebnis: *Glyphe sehen → antippen → sofortiges Feedback → nächste*.

**In Scope (MVP):** Kapitel 1–5 des Initial-Prompts:

1. Alphabet als System (Referenzansicht, traditionelle Reihen, Devanagari optional)
2. Glyphe → Wylie
3. Wylie → Glyphe
4. Vokale (i, u, e, o + inhärentes a), erst auf ཀ, dann verallgemeinert
5. Audio → Glyphe/Silbe (gebündelte statische Clips)

**Nur vorbereitet, nicht gebaut:** Kapitel 6 (Silbenstruktur) und 7 (einfache Wörter). Das
Datenmodell trägt dafür bereits `analysis` (Positionen aus `tz.analyse`) und `kind`.

**Out of scope:** alles aus „Out of scope“ des Initial-Prompts (Accounts, Backend, Spracherkennung,
Gamification usw.).

## 2. Architektur

```
content/curriculum.toml ──┐
content/audio.toml ───────┤  uv run learn-tibetan build-content
                          ▼  (Python, nutzt phonetics.tz + phonetics.wylie)
web/src/content/curriculum.json  (generiert, committed)
                          ▼
React-App (web/) ── Engine (pure TS) ── localStorage
        └── Service Worker (Workbox) precacht App, Font, Audio → offline
```

- **Python nur zur Build-Zeit.** Die App liest statisches JSON. Wylie/TZ werden nie von Hand in
  Content oder UI geschrieben.
- **Repo-Layout:** Das vorhandene uv-Projekt (`pyproject.toml`, `src/learn_tibetan/`) bleibt und wird
  zur Content-Pipeline. Die Web-App liegt in `web/` (eigenes `package.json`), damit sich Python-
  und Node-`src/` nicht in die Quere kommen.
- **Stack:** React 19 + TypeScript + Vite, `vite-plugin-pwa` (generateSW), Vitest. Kein
  Router-Paket (kleiner Hash-/State-Router), keine State-Library (`useReducer` + Context), kein
  UI-Framework, plain CSS mit CSS-Variablen.
- **Font:** selbst gehostete Tibetan-Schrift als woff2 in `web/public/fonts/`, vom Service Worker
  precacht. Erste Wahl **Noto Serif Tibetan** (SIL OFL 1.1), Alternative **Jomolhari** (OFL);
  Entscheidung nach Sichtprüfung auf dem Handy, dokumentiert in `docs/decisions.md`.

## 3. Content-Quelle (`content/curriculum.toml`)

Von Hand gepflegt, mit Kommentaren für fachliche Unsicherheit. Enthält nur, was **nicht**
generierbar ist:

```toml
[[groups]]
id = "velar"
order = 1
label_de = "Kehllaute"
linguistic = "velar (traditionell: guttural)"
note_de = "…"
letters = [
  { tibetan = "ཀ", devanagari = "क" },
  { tibetan = "ཁ", devanagari = "ख" },
  …
]

[vowels]
signs = [ { sign = "", name_de = "inhärentes a" }, { sign = "ི", name_de = "gi gu (i)" }, … ]

[confusables]           # Distraktor-Hinweise, ausdrücklich vorläufig
visual = [["པ","ཕ"], ["བ","ཝ"], …]
wylie  = [["ca","tsa"], ["cha","tsha"], ["ja","dza"], ["zha","sha"], ["za","sa"], ["na","nya","nga"]]

[audio_equivalent]      # Laute, die im Audio nicht unterscheidbar sein könnten (Kurationsdaten)
groups = []
```

Traditionelle Reihen (je 4): ཀཁགང · ཅཆཇཉ · ཏཐདན · པཕབམ · ཙཚཛཝ · ཞཟའཡ · རལཤས · ཧཨ.
Labels Reihe 1–4 wie im Initial-Prompt (Kehllaute, Gaumenlaute, Zahn-/Zahndammlaute,
Lippenlaute) mit technischem Zweitlabel. Reihe 5 „Zischlaute (tibetische Ergänzung)“; Reihen 6–8
neutrale Labels. Eine kurze Notiz erklärt die indische Herkunft und dass heutiges Tibetisch nicht
klassisches Sanskrit ist.

**Devanagari-Parallelen:** sicher für Reihen 1–4 sowie ཡ र ल श स ह अ (य र ल श स ह अ) und ཝ (व).
Für ཙ ཚ ཛ nur mit Notiz („so werden च छ ज in Sanskrit-Umschrift geschrieben“). ཞ ཟ འ ohne
Parallele.

## 4. Generiertes Datenmodell (`curriculum.json`)

```ts
type Item = {
  id: string                // stabil, z. B. "l-ka", "v-ki"
  kind: 'letter' | 'vowel-form'          // später: 'syllable' | 'word'
  tibetan: string           // NFC
  wylie: string             // generiert: wylie.syllable()
  tz: string                // generiert: tz.render(…, "tz-aktuell")
  order: number
  groupId?: string
  baseId?: string           // vowel-form -> Grundbuchstabe
  vowel?: 'a' | 'i' | 'u' | 'e' | 'o'
  devanagari?: string
  devanagariNote?: string
  analysis: { prefix, superscript, root, subscripts, vowel, suffix, postsuffix }  // für Kap. 6
  audio?: { src: string; source: string; dialect: string; status: 'candidate' | 'approved' }
}
type Group = { id; order; labelDe; linguistic?; noteDe?; itemIds: string[] }
type Lesson = {
  id; chapter: 1|2|3|4|5; titleDe
  introItemIds?: string[]   // Reihen-/Vokalkarte vor dem ersten Drill
  newItemIds: string[]      // Schwerpunkt dieser Lektion
  modes: QuizMode[]
}
type QuizMode = 'tib-wylie' | 'wylie-tib' | 'audio-tib'
type Curriculum = {
  meta: { generatedAt; engine: { tz: string; wylie: string; tzVariant: 'tz-aktuell' } }
  groups; items; lessons; confusables; audioEquivalent
}
```

TZ wird nur in der Variante `tz-aktuell` erzeugt (Variante steht in `meta`). Weitere Varianten
erst bei Bedarf.

## 5. Lernpfad (Lektionen)

Linear, jede Lektion schaltet die nächste frei.

| # | Kapitel | Lektion | Items | Modus |
|---|---|---|---|---|
| 1–16 | 2/3 | Reihe *r* (r = 1…8): erst Intro-Karte + Glyphe→Wylie, dann Wylie→Glyphe | 4 Buchstaben je Reihe | `tib-wylie`, dann `wylie-tib` |
| 17 | 4 | Vokale auf ཀ (ཀ ཀི ཀུ ཀེ ཀོ) | 5 | beide |
| 18 | 4 | Vokale auf Reihen 1–4 | 16 × 5 | beide |
| 19 | 4 | Vokale auf allen Buchstaben | 30 × 5 | beide |
| 20 | 5 | Audio: Buchstaben Reihen 1–4 | mit Audio | `audio-tib` |
| 21 | 5 | Audio: restliche Buchstaben | mit Audio | `audio-tib` |
| 22 | 5 | Audio: Vokalformen auf ཀ | mit Audio | `audio-tib` |

Kapitel 1 ist die Alphabet-Referenz plus die Intro-Karten. Audio-Lektionen enthalten nur Items mit
Clip, der nicht `rejected` ist; ohne Clips wird die Lektion als „Audio folgt“ angezeigt.
Einstellung „Alle Lektionen freischalten“ für freies Üben.

## 6. Quiz-Engine (pure TypeScript, `web/src/engine/`)

### 6.1 Fortschritt pro (Item, Modus)

`{ seen, correct, box: 0..5, lastSeenAt: questionCounter, mistakes: number[] (letzte 5 Zeitstempel) }`

- richtig → `box + 1` (max 5); falsch → `box = max(0, box − 2)` und Item kommt nach **2–3** Fragen
  erneut (Fehler-Warteschlange).
- Lektion gemeistert, wenn alle `newItemIds` in allen Lektionsmodi `box ≥ 3`. Alle Schwellwerte
  stehen in `engine/config.ts`.

### 6.2 Auswahl der nächsten Frage

1. Fällige Fehler-Warteschlange hat Vorrang.
2. Sonst gewichtete Zufallswahl aus Pool = neue Items der aktuellen Lektion + alle früher
   freigeschalteten Items desselben Modus. Gewicht ≈ `(6 − box)²`, neue Items × 2, die letzten
   2 gezeigten Items ausgeschlossen. Nicht gleichverteilt.
3. Seeded RNG, damit Tests deterministisch sind.

### 6.3 Distraktoren

Kandidaten = Items derselben `kind` (für `vowel-form`: bevorzugt gleicher Grundbuchstabe).
Priorität: (1) gleiche Reihe/Gruppe bzw. gleicher Grundbuchstabe, (2) `confusables.visual`,
(3) `confusables.wylie`, (4) andere freigeschaltete Items, (5) beliebige Items derselben Art.
Innerhalb einer Stufe zufällig. Immer genau 4 eindeutige Antworten.

### 6.4 Mehrdeutigkeit (allgemeine Regel)

Jeder Modus hat eine **Prompt-Repräsentation** P und eine **Antwort-Repräsentation** A
(`tib-wylie`: P = tibetan, A = wylie; `wylie-tib`: P = wylie, A = tibetan; `audio-tib`:
P = Audio-Schlüssel, A = tibetan). Ein Distraktor *d* ist nur gültig, wenn `P(d) ≠ P(Ziel)` und
`A(d) ≠ A(Ziel)`. Der Audio-Schlüssel ist die Clip-Datei, wobei Items derselben
`audioEquivalent`-Gruppe als gleich gelten. Gibt es keine 3 gültigen Distraktoren, wird die Frage
nicht gestellt. Damit sind z. B. ཅ/ཆ (beide TZ *tscha*) in einem künftigen TZ-Modus automatisch
nie zusammen in einer Frage, ohne Sonderfälle.

## 7. Audio

- **Runtime:** nur statische Dateien (`web/public/audio/<id>.mp3`), precacht, Abspielen über ein
  kleines `audio.ts` (`play(item)`, Preload, Lautstärke aus Settings). Kein Cloud-TTS.
- **Manifest** `content/audio.toml`: pro Item `file`, `source` (z. B. `mms-tts-bod` + Version,
  `manual`), `dialect`, `status` (`candidate` | `approved` | `rejected`), `note`. Der Content-Build
  übernimmt das in `item.audio`.
- **Kandidatenerzeugung (Dev-Tool):** `tools/audio/` mit `facebook/mms-tts-bod` (VITS, lokal,
  eigene uv-Dependency-Gruppe `audio`, nicht im Default-Install). **Vor dem Einsatz prüfen:**
  Verfügbarkeit, Lizenz (MMS-Modelle stehen nach meinem Stand unter CC-BY-NC 4.0, für privaten
  Prototyp vertretbar, nicht für Veröffentlichung), Zielvarietät (Zentraltibetisch), Qualität bei
  Einzelbuchstaben. Fallback: Trägersilbe/-wort oder manuelle Aufnahme durch den Owner.
- **Kuration:** einfache Prüfansicht in der App (Liste aller Clips mit Play-Button und Status), Status
  wird im Manifest von Hand gesetzt. Jeder Clip ist durch Datei-Ersatz austauschbar.
- Keine Spracherkennung, keine Aussprachebewertung.

## 8. Screens und UX

- **Home:** Weiterlernen (aktuelle Lektion), Alles üben, Schwieriges wiederholen (nur wenn
  vorhanden), Alphabet, Einstellungen. Kapitelliste 1–5 mit kleinem Fortschrittsbalken.
- **Quiz:** schmaler Fortschrittsbalken der Lektion oben; Prompt groß (Einzelglyphe ~110–140 px,
  Wylie groß in Latin-Mono/Serif); 4 große Antwortflächen im unteren Daumenbereich (2×2 oder 4×1
  je nach Inhalt). Richtig → kurzer Gold-Akzent, nach ~350 ms weiter. Falsch → Auswahl rot, richtige
  Antwort deutlich markiert, automatisch weiter nach ~1,5 s, Tippen überspringt die Wartezeit. Kein
  „Weiter“-Button, keine Modals. Doppel-Submits gesperrt. Optional `navigator.vibrate`.
  Tastatur: 1–4 / Pfeile + Enter, Leertaste spielt Audio erneut.
- **Intro-Karte:** die neue Reihe (4 Glyphen, Wylie, Gruppenlabel, optional Devanagari/TZ, Audio),
  ein Button „Los“.
- **Alphabet-Referenz:** 8 Reihen als Raster wie in der Screenshot-Vorlage, pro Zelle Glyphe +
  Wylie, optional TZ/Devanagari (Settings), Antippen öffnet ein kleines Detail (Gruppe, Notiz,
  Audio). Darunter die Vokalzeichen auf ཀ.
- **Einstellungen:** Devanagari-Parallelen zeigen, TZ-Aussprache in Referenzansichten zeigen, Audio
  automatisch abspielen, Lautstärke, alle Lektionen freischalten, Fortschritt zurücksetzen
  (mit Bestätigung).
- **Qualität:** semantische Buttons, sichtbare Fokuszustände, `prefers-reduced-motion`,
  Kontrast ≥ WCAG AA, Portrait-First, kein Desktop-Layout auf Mobile gequetscht.

## 9. Visuelle Richtung

Palette aus dem Initial-Prompt als CSS-Variablen: Robenrot `#6F2634` (Struktur/Akzent),
Safran `#D39A28` und Senfgold `#B77A20` (Fortschritt, Auswahl, Highlights), Creme `#F4EBDD`
(Flächen), Dunkelbraun `#30231F` (Text), Pflaume `#6C496C` nur als winziger Akzent. Feedback-Farben
aus der Palette abgeleitet (richtig = Gold/Olivgold, falsch = gedecktes Rot), kein Material-Blau/Grün.
Latin-UI zurückhaltend (System-Sans), Tibetisch ist der visuelle Fokus.

## 10. Persistenz

`localStorage`-Schlüssel `lt.v1.progress` und `lt.v1.settings`. Bei Versionswechsel wird verworfen,
nicht migriert (Prototyp, siehe AGENTS.md).

## 11. Tests (minimal, gezielt)

- Python: 62 Referenztests (unverändert) + 1 Testdatei Content-Build (30 Buchstaben in
  traditioneller Ordnung, 8 Gruppen, eindeutige IDs/Wylie, Vokalformen korrekt zusammengesetzt).
- Vitest: Distraktoren (4 eindeutige Antworten, Mehrdeutigkeitsregel, Prioritäten), Mastery-Update und
  Fehler-Warteschlange, Persistenz-Roundtrip.
- Kein E2E. PWA/Offline einmal manuell per `npm run preview` geprüft und im Log dokumentiert.

## 12. Annahmen mit pädagogischer/architektonischer Wirkung

1. „Nur bis Schritt 5“ = Curriculum-Kapitel 1–5. Kapitel 6/7 nur im Datenmodell vorbereitet.
2. Wylie-Antworten werden in EWTS ohne Diakritika gezeigt (`ca`, `'a`, `a`), genau wie die Engine
   sie liefert.
3. Kapitel 2 und 3 werden pro Reihe verschränkt statt nacheinander über alle 30 Buchstaben
   (schnellere bidirektionale Festigung; Kapitelzuordnung bleibt in der UI sichtbar).
4. TZ wird im MVP nur angezeigt (Referenz/Intro), nicht abgefragt.
5. Audio-Zielvarietät: Zentraltibetisch (Lhasa-nah), wie sie MMS `bod` liefert, sofern
   bestätigt. Abweichungen werden pro Clip im Manifest vermerkt.
6. Es gibt keine UI-Referenzgrafik unter `references/ui/`; das Design folgt der Textbeschreibung.
