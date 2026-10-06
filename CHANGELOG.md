# Changelog

Alle nennenswerten Änderungen an diesem Projekt. Format nach
[Keep a Changelog](https://keepachangelog.com/de/1.1.0/), Versionierung nach
[Semantic Versioning](https://semver.org/lang/de/).

## [Unreleased]

### Added

- Ausspracheinfos hinter ⓘ: pro Buchstabe Behauchung, Ton und deutscher Aussprachehinweis
  (Detailansicht, Intro-Karte, Oops-Panel mit Vergleich richtige/gewählte Antwort).
- Vokale: Klangbeschreibung, Zeichenname (mit Aufnahme) und Beispielwort (མེ ཆུ རི སོ, mit Aufnahme).
- „Hintergrundwissen“ im Alphabet (ⓘ oben rechts): inhärentes a & Tsheg, Behauchung, Ton,
  ག ཇ ད བ (g oder kh?), Schrift/Wylie/TZ/Klang.
- Eigene Aufnahmen des Owners für alle 30 Buchstaben und ཨི ཨུ ཨེ ཨོ, geschnitten und freigegeben;
  Hörlektionen a1–a3 (a3: Vokale auf ཨ) vollständig spielbar.
- `curate.py split`: zerlegt eine Aufnahme mit mehreren Silben (z. B. eine ganze Reihe) an den
  Pausen, verwirft Klicks/Atmer, exportiert normalisierte Einzelclips.
- Feedback-Töne (synthetisiert, Einstellung „Feedback-Töne“).

### Changed

- Falsche Antwort: Duolingo-artiges Panel „Oops, nicht ganz.“ mit richtiger Lösung, eigener Wahl,
  TZ-Aussprache und Anhören; weiter **nur per „Weiter“** (oder Enter), kein Timer mehr.
- Hörlektion a3: Vokale auf ཨ statt auf ཀ (passend zu den Aufnahmen).

### Added

- Einstellung „Aussprache von ག ཇ ད བ“ (A: wie ཁ ཆ ཐ ཕ mit tiefem Ton / B: weich g dsch d b);
  Audio-Clips können je Variante hinterlegt werden (`curate.py split … --variant A|B`).

### Changed

- ག ཇ ད བ: Infotexte erklären die zwei verbreiteten Aussprachen konkret (A: wie ཁ/ཆ/ཐ/ཕ mit
  tiefem Ton; B: weich g/dsch/d/b) statt „behaucht“ pauschal; Behauchung dort „je nach Aussprache“.

### Fixed

- Hörübungen stumm/kaum hörbar: ersetzte Clips mit gleichem Dateinamen kamen aus dem Cache
  (Speicher-Cache des Audio-Elements bzw. Service Worker). Audio-URLs tragen jetzt einen Inhalts-Hash.

### Removed

- MMS-TTS-Kandidatenclips (vom Owner als unbrauchbar bestätigt).

- README: Starten, Tests, Content-Repräsentation, Transliteration, Audio, PWA-Installation.

## [0.2.0] — 2026-10-06

Kapitel 4 (Vokale) und 5 (Hören, Infrastruktur).

### Added

- Audio (Kapitel 5): statische Clips (`web/public/audio/`), precacht; Audio-Modul, Play-Buttons in
  Detailansicht und Intro, Modus „Hören → Zeichen“ (Lektionen a1–a3) mit Auto-Play und Leertaste,
  Vorspielen der richtigen Antwort nach dem Antippen (Einstellung „Audio automatisch“).
- Gelernt wird nur mit freigegebenen Clips (`status = "approved"`); KI-Kandidaten sind nur in der
  Prüfansicht (`#/audio-review`, verlinkt in den Einstellungen) hörbar und dort markierbar.
- `tools/audio/generate.py` (MMS-TTS `facebook/mms-tts-bod`, optionale uv-Gruppe `audio`, CPU-Torch)
  und `tools/audio/curate.py` (Import eigener Aufnahmen mit Trim/Loudness/mp3, Übernahme der Prüfergebnisse).
- 34 MMS-Kandidaten-Clips (alle Buchstaben + Vokale auf ཀ), Status `candidate`.

- Kapitel 4 (Vokale): Vokal-Intro (ཀ ཀི ཀུ ཀེ ཀོ mit tibetischen Vokalnamen), Lektion „Vokale auf ཀ“
  in beiden Richtungen, Verallgemeinerung auf Reihen 1–4 und alle Buchstaben (Leserichtung).
- Pro Lektion einstellbare Meisterungsschwelle (`mastery: {box, share}`).

### Fixed

- Tibetisch in UI-Texten (Überschriften, Buttons) wurde als Tofu dargestellt; Jomolhari steht jetzt
  per `unicode-range` vorne in der UI-Font-Kette.
- Ungleich hohe Label-Bänder im Raster.

## [0.1.0] — 2026-10-06

Erste spielbare Version: Kernerlebnis Zeichen ↔ Wylie (Kapitel 1–3).

### Added

- Quiz-Engine (`web/src/engine/`): Box-Modell pro Item und Richtung, Fehler kehren nach 2–3 Fragen
  zurück, gewichtete statt gleichverteilte Auswahl, kumulative Wiederholung, Distraktoren nach Reihe /
  Verwechslungslisten / Bekanntem, allgemeine Mehrdeutigkeitsregel, seeded RNG; Vitest-Tests.
- Quiz-Screen: große Glyphe, vier Daumen-Antworten, Auto-Weiter nach richtig (350 ms) bzw. falsch
  (1,5 s, Tippen überspringt), Lösung bei Fehlern, Tastatur 1–4/Enter/Esc, Haptik, kein Doppel-Submit.
- Intro-Karte pro neuer Reihe, Abschlusskarte mit „Weiter“, lineare Freischaltung (16 Konsonanten-Lektionen).
- Home mit Lernpfad pro Reihe (beide Richtungen), „Alles üben“, „Schwieriges wiederholen“.
- Fortschritt in localStorage (`lt.v1.progress`), Reset in den Einstellungen.
- `tools/shot.mjs`: abhängigkeitsfreier Headless-Chrome-Treiber (CDP) für UI-Checks.

- Web-App-Gerüst (`web/`): Vite + React + TypeScript, PWA (Manifest, Icons, Service Worker mit
  Precache inkl. Font), Theme in Roben-/Safran-Palette, Font Jomolhari.
- Alphabet-Referenz (Kapitel 1): 8 traditionelle Reihen im 4er-Raster, Wylie-Label, optional
  TZ/Devanagari, Detailansicht pro Zeichen, Vokalzeichen auf ཀ, Hinweis zur indischen Herkunft.
- Einstellungen (Devanagari, TZ, Audio, Lautstärke, alle Lektionen freischalten, Reset).
- Content-Pipeline: `content/curriculum.toml` (8 traditionelle Reihen, 30 Buchstaben,
  Devanagari-Parallelen/-Notizen, Vokalzeichen, vorläufige Verwechslungslisten) und
  `content/audio.toml` → `uv run learn-tibetan build-content` → `web/src/content/curriculum.json`
  (150 Items mit generiertem Wylie/TZ/Silbenanalyse, 22 Lektionen).
- Projektgerüst (uv-Python-Projekt für die Content-Pipeline).
- Transliterations-Referenzpaket (Transfer 2026-10-06) entpackt und einsortiert
  (`references/transliteration/`, Index in dessen `README.md`).
- Referenz-Engine Tibetisch → Wylie/EWTS und Tibetisch → TZ-Aussprache unter
  `src/learn_tibetan/phonetics/` samt 62 Referenztests (`tests/phonetics/`).
- Arbeitsregeln (`AGENTS.md`, `CLAUDE.md`), Spec, Implementierungsplan und Ausführungsprompt
  (`specs_plans_prompts/01_02`–`01_04`), Engineering-Log und Entscheidungslog (`docs/`).
