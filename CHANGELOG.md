# Changelog

Alle nennenswerten Änderungen an diesem Projekt. Format nach
[Keep a Changelog](https://keepachangelog.com/de/1.1.0/), Versionierung nach
[Semantic Versioning](https://semver.org/lang/de/).

## [Unreleased]

### Added

- Projektgerüst (uv-Python-Projekt für die Content-Pipeline).
- Transliterations-Referenzpaket (Transfer 2026-10-06) entpackt und einsortiert
  (`references/transliteration/`, Index in dessen `README.md`).
- Referenz-Engine Tibetisch → Wylie/EWTS und Tibetisch → TZ-Aussprache unter
  `src/learn_tibetan/phonetics/` samt 62 Referenztests (`tests/phonetics/`).
- Arbeitsregeln (`AGENTS.md`, `CLAUDE.md`), Spec, Implementierungsplan und Ausführungsprompt
  (`specs_plans_prompts/01_02`–`01_04`), Engineering-Log und Entscheidungslog (`docs/`).
