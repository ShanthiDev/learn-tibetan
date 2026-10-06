# Changelog

Alle nennenswerten Änderungen an diesem Projekt. Format nach
[Keep a Changelog](https://keepachangelog.com/de/1.1.0/), Versionierung nach
[Semantic Versioning](https://semver.org/lang/de/).

## [Unreleased]

### Added

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
