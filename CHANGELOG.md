# Changelog

Alle nennenswerten Änderungen an diesem Projekt. Format nach
[Keep a Changelog](https://keepachangelog.com/de/1.1.0/), Versionierung nach
[Semantic Versioning](https://semver.org/lang/de/).

## [Unreleased]

### Added

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
