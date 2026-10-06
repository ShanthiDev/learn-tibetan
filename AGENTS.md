# AGENTS.md — Arbeitsregeln für dieses Repository

Gilt für jeden Agenten (und Menschen), der hier arbeitet. Bei Konflikt mit einem Prompt gewinnt
der ausdrückliche Wunsch des Owners; sonst gilt diese Datei.

## 1. Kontext: privater, lokaler Prototyp

- Wir bauen **from scratch** einen privaten Prototypen, kein Produktionssystem.
- Keine Migrationen, keine Abwärtskompatibilität, kein Legacy-Erhalt, keine Konsistenzprüfungen
  „für alle Fälle“. Ändert sich ein Datenformat (z. B. localStorage), wird die Version erhöht und
  alter Stand verworfen.
- Lieber einfach und direkt umbauen als Schichten für hypothetische Zukunft einziehen.

## 2. Token-bewusst arbeiten

Tokens sind teuer. Konkret:

- Nur lesen, was für den nächsten Schritt nötig ist. Bekannte Dateien nicht erneut lesen;
  große Dateien gezielt (Ausschnitt, `grep`) statt komplett.
- Generierte Dateien (`web/src/content/curriculum.json`, Lockfiles, Build-Output) nie komplett in
  den Kontext holen; höchstens `head`/`jq`-Ausschnitte.
- Befehlsausgaben kurz halten (`-q`, `| tail`, `--silent`).
- Tests **gezielt** für den geänderten Bereich ausführen. Die Gesamtsuite nur vor einem
  Meilenstein-Commit, und nur weil sie schnell ist (Python ~1 s, Vitest wenige Sekunden).
- Keine Regressionstest-Orgien, keine E2E-/Screenshot-Tests, keine Coverage-Jagd, solange sie keine
  konkrete Frage beantworten.
- Keine Subagenten ohne klaren Bedarf. Keine Variantenvergleiche, die niemand angefragt hat.
- Entscheiden statt aufzählen: bei Wahlmöglichkeiten eine Empfehlung umsetzen und in
  `docs/decisions.md` festhalten.

## 3. Tests: wo sie echtes Vertrauen kaufen

Ja: Transliteration/TZ-Engine (die 62 Referenztests bleiben erhalten), Content-Build (Reihenfolge,
Gruppen, Eindeutigkeit), Distraktoren (Eindeutigkeit, keine mehrdeutigen Fragen), Mastery-Update,
Persistenz-Roundtrip.
Nein: triviale UI-Komponenten, Snapshot-Tests, Tests, die nur Implementierung spiegeln.

## 4. Dokumentation

| Datei | Zweck | Wann |
|---|---|---|
| `CHANGELOG.md` | Nutzersicht, [Keep a Changelog](https://keepachangelog.com/de/1.1.0/), SemVer | jede nennenswerte Änderung unter `[Unreleased]`; Version beim Meilenstein |
| `docs/engineering-log.md` | ausführliches Arbeitsprotokoll: Ziel, Vorgehen, Befunde, Probleme, Sackgassen, nächste Schritte | jede Arbeitssitzung / jeder Schritt |
| `docs/decisions.md` | Entscheidungen (ADR-light): Kontext, Entscheidung, Begründung, verworfene Alternativen, **Sackgassen** | sobald eine Entscheidung fällt oder ein Weg scheitert |
| `specs_plans_prompts/` | Specs, Pläne, Prompts, nummeriert `NN_MM_Titel.md` | bei neuen Plänen; alte bleiben als Historie |
| `README.md` | Starten, Testen, Content, Transliteration, Audio, PWA | aktuell halten |

Vor einem neuen Ansatz kurz `docs/decisions.md` (Abschnitt Sackgassen) prüfen, damit gescheiterte
Wege nicht erneut beschritten werden.

## 5. Abschluss jedes Arbeitsschritts

1. Betroffene Tests grün.
2. `CHANGELOG.md`, `docs/engineering-log.md`, ggf. `docs/decisions.md`/`README.md` aktualisiert.
3. Commit (Conventional Commits, englisch, z. B. `feat(quiz): ...`), danach `git status` sauber.
   Der nächste Schritt beginnt immer mit sauberem Working Tree.

## 6. Fachliche Leitplanken (Tibetisch)

- Vier Repräsentationen bleiben **getrennt**: tibetische Schreibung, Wylie/EWTS, TZ-Aussprache,
  Audio. Nie Wylie durch Lautschrift ersetzen oder umgekehrt.
- Wylie und TZ werden **generiert** (`src/learn_tibetan/phonetics/`), nie von Hand in Content oder UI
  gepflegt. Die Engine stammt aus dem Transferpaket; Regeländerungen nur mit Test und Eintrag in
  `docs/decisions.md`.
- Fachliche Unsicherheit (Devanagari-Parallelen, Verwechslungspaare, Audio-Gleichklang) gehört in
  Daten (`content/`), mit Notiz, nicht in Logik.
- Keine Quizfrage mit mehrdeutiger Antwort (siehe Spec, Abschnitt Mehrdeutigkeit).
- Die Browser-Runtime braucht kein Python; Python läuft nur zur Build-/Entwicklungszeit.

## 7. Rechte und große Dateien

- `references/transliteration/` ist internes Material (Ursprung proprietär, TZ-Scans nur intern
  freigegeben, DILA ungeklärt). Nicht veröffentlichen, nicht als Paket herausgeben.
- Große Referenzdateien (Zip, PDFs, DILA-Index, XLSX/JSON-Mappings, Audio-Kandidaten-Cache) sind
  gitignored und werden nie committed. Neue große Dateien vor dem Commit prüfen (`git status`,
  Größe) und ggf. ignorieren.
- Generierter App-Content (`web/src/content/curriculum.json`) und kuratierte Audio-Dateien
  werden committed, damit die App ohne Python baut.

## 8. Konventionen

- UI-Sprache Deutsch. Code, Bezeichner, Commit-Messages Englisch. Doku Deutsch.
- Einfache, inspizierbare Daten und Logik vor cleveren Abstraktionen. Wenige Abhängigkeiten.
- Owner nur fragen, wenn eine Entscheidung das Produkt wesentlich verändert; sonst entscheiden und
  dokumentieren.

## 9. Repo-Karte und Befehle

```
content/                 Quell-Curriculum (von Hand gepflegt, TOML) + Audio-Manifest
src/learn_tibetan/       Python: Build-Pipeline; phonetics/ = Referenz-Engine (tz, wylie)
tests/                   Python-Tests (phonetics/ = Referenztests aus dem Transferpaket)
web/                     React + TypeScript + Vite PWA
  src/content/           generiertes curriculum.json (committed)
  public/audio/          kuratierte Audio-Clips
tools/audio/             Entwicklungs-Tools zur Audio-Kandidatenerzeugung
references/              Referenzmaterial (teilweise gitignored)
docs/                    engineering-log.md, decisions.md, weitere Doku
specs_plans_prompts/     Specs, Pläne, Prompts
```

```bash
uv run pytest -q                       # Python-Tests
uv run learn-tibetan build-content     # content/ -> web/src/content/curriculum.json
cd web && npm run dev                  # Dev-Server
cd web && npm test                     # Vitest
cd web && npm run build && npm run preview   # PWA-Build lokal prüfen
```

Netzwerk: In dieser WSL-Umgebung fällt DNS zeitweise aus. Python-Pakete notfalls mit
`uv ... --offline` aus dem Cache holen.
