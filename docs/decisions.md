# Entscheidungen und Sackgassen

ADR-light. Neueste Einträge unten. Format: Kontext → Entscheidung → Begründung → Alternativen.
Sackgassen (gescheiterte Wege) stehen gesammelt am Ende, damit sie nicht erneut beschritten werden.

## D-001 — Repo-Layout: Python-Pipeline im Root, Web-App in `web/` (2026-10-06)

- **Kontext:** `uv init` hat bereits `pyproject.toml` + `src/learn_tibetan/` angelegt; die
  React-App braucht ebenfalls ein `src/`.
- **Entscheidung:** Python bleibt im Root (Content-Pipeline + Referenz-Engine), Web-App in `web/`.
- **Begründung:** kein Umzug des Bestehenden, klare Trennung Build-Zeit (Python) / Runtime (TS).
- **Alternativen:** Python nach `pipeline/` verschieben (unnötige Churn); Monorepo-Tooling (Overkill).

## D-002 — Referenz-Engine unverändert übernommen (2026-10-06)

- **Entscheidung:** `tz.py`/`wylie.py` aus dem Transferpaket nach `src/learn_tibetan/phonetics/`;
  einzige Änderung: Importpfad `atp.phonetics` → `learn_tibetan.phonetics`. Tests ebenso (plus
  angepasste Fixture-/DILA-Pfade). 62 passed.
- **Begründung:** Initial-Prompt verlangt, die Regeln nicht neu zu erfinden; README des Pakets
  empfiehlt genau diese Extraktion.
- **Folge:** Regeländerungen nur mit Test und eigenem Eintrag hier.

## D-003 — Große/rechtlich eingeschränkte Referenzdateien gitignored (2026-10-06)

- **Entscheidung:** nicht committed: Original-Zip, TZ-PDF-Scans, DILA-Index (7 MB), Mapping-JSON
  (623 KB, inhaltsgleich mit committeter CSV), Korpus-XLSX. Committed: Code, Tests, Doku,
  Evidenz-Textdateien, Mapping-CSV.
- **Begründung:** Größe und Rechte (proprietärer Ursprung, Scans nur intern freigegeben, DILA ungeklärt).
  Der DILA-Wylie-Test wird ohne Index automatisch übersprungen.

## D-004 — Content-Quelle als TOML, generiertes JSON committed (2026-10-06)

- **Entscheidung:** `content/curriculum.toml` (von Hand, kommentierbar) → Python-Build →
  `web/src/content/curriculum.json` (committed).
- **Begründung:** `tomllib` ist stdlib (keine Abhängigkeit), Kommentare für fachliche
  Unsicherheit; App baut ohne Python.
- **Alternativen:** YAML (braucht PyYAML), Content direkt in TS (würde Wylie/TZ-Handpflege verleiten).

## D-005 — Mehrdeutigkeit über allgemeine Repräsentations-Kollision (2026-10-06)

- **Entscheidung:** Distraktor gültig nur, wenn er sich vom Ziel in Prompt- *und*
  Antwort-Repräsentation unterscheidet; sonst Frage verwerfen (Spec §6.4).
- **Begründung:** Engine-Probe zeigt TZ-Kollisionen ཅ/ཆ (tscha), ཞ/ཤ (scha), ཟ/ས (sa), འ/ཨ (a).
  Eine allgemeine Regel deckt TZ- und Audio-Modi ohne Sonderfälle ab.

## D-006 — Kapitel 2 und 3 pro Reihe verschränkt (2026-10-06)

- **Entscheidung:** Lernpfad je Reihe: Glyphe→Wylie, dann Wylie→Glyphe, dann nächste Reihe.
- **Begründung:** frühere bidirektionale Festigung (`ཅ ↔ ca`), kleine Gruppen, kumulative Wiederholung.
- **Alternative:** erst alle 30 in Richtung 1, dann alle in Richtung 2 (längere Durststrecke).

## Sackgassen

- *(noch keine)*
