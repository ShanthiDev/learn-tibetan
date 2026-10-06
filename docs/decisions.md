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

## D-007 — Tibetan-Font: Jomolhari (2026-10-06)

- **Kontext:** Spec nannte Noto Serif Tibetan als erste Wahl, Jomolhari als Alternative.
- **Vergleich:** beide via `@fontsource/*` (OFL-1.1), Headless-Chrome-Rendering von ཀ ཅ ཉ, Reihen,
  Vokalformen und dem Stapel བསྒྲུབས: beide setzen Stapel und Vokale korrekt.
- **Entscheidung:** **Jomolhari** (Christopher Fynn, SIL OFL 1.1), eingebunden über
  `@fontsource/jomolhari/tibetan-400.css`, woff2 362 KB, vom Service Worker precacht.
- **Begründung:** kalligrafischer, kräftiger Uchen-Duktus nah an Pecha-Drucken und an der
  UI-Vorlage; Noto (160 KB) wirkt dünner/technischer. Die Größe ist für eine PWA vertretbar.
- **Folge:** Jomolhari-Glyphen sind relativ zum em klein → Schriftgrößen entsprechend höher
  (Raster `min(22vw, 112px)`). Lizenztext liegt im npm-Paket (`node_modules/@fontsource/jomolhari/LICENSE`).

## D-008 — Stack-Versionen und Werkzeuge (2026-10-06)

- Vite 8, React 19, TypeScript 7, Vitest 5, vite-plugin-pwa 2 (generateSW). Kein Router-/State-Paket.
- App-Icons (ཨ in Safran auf Robenrot) und Screenshots werden mit dem lokal vorhandenen
  Playwright-Headless-Chromium (`~/.cache/ms-playwright/chromium_headless_shell-1234/…`)
  gerendert, ohne zusätzliche npm-Abhängigkeit. Aufruf:
  `chrome-headless-shell --no-sandbox --window-size=390,700 --virtual-time-budget=3000 --screenshot=out.png URL`.

## D-009 — Font selbst gehostet statt Fontsource-CSS (2026-10-06)

- **Kontext:** Fontsource setzt `font-display: swap`. Systemfonts haben meist kein Tibetisch → beim
  ersten Rendern Tofu-Kästchen statt Glyphe (im Screenshot sichtbar).
- **Entscheidung:** `web/public/fonts/jomolhari-tibetan.woff2` + OFL-Text daneben, eigene
  `@font-face` mit `font-display: block` und `unicode-range` Tibetisch, `<link rel="preload">` in
  `index.html`. Jomolhari zusätzlich am Ende der UI-Font-Kette, damit Tibetisch in UI-Texten
  (Buttons, Labels) nie Tofu wird. Fontsource-Paket entfernt.

## D-010 — Lernpfad-Details (2026-10-06)

- Lektionen sind auch per URL erreichbar (`#/learn/<id>`), gesperrte nur über die Home-Buttons
  verhindert. Kein Guard: privater Prototyp.
- Pool einer Lern-Session = neue Items (Gewicht ×2) + alle Items früherer *freigeschalteter* Lektionen.
- „Schwieriges“ = Fehler in den letzten 200 Fragen oder Trefferquote < 70 % bei ≥ 2 Versuchen.
- Wylie in der UI-Sans statt Monospace (Monospace wirkte klobig, Apostroph bleibt gut sichtbar).

## D-011 — Vokal-Verallgemeinerung: nur Leserichtung, leichtere Meisterung (2026-10-06)

- **Kontext:** Spec sah v2 (80 Formen) und v3 (150 Formen) in beiden Richtungen mit Box 3 vor →
  480 bzw. 900 richtige Antworten bis zur Freischaltung; Kapitel 5 wäre dahinter blockiert.
- **Entscheidung:** v1 (Vokale auf ཀ) beide Richtungen, Box 3, alle Items. v2 nur Zeichen→Wylie,
  Box 2 für 80 % der Formen (~130 Antworten). v3 nur Zeichen→Wylie, Box 1 für 80 % (~60–120
  Antworten, da v2-Formen schon zählen). Umsetzung als optionales `mastery` je Lektion.
- **Begründung:** Ziel ist Lesen; das Vokalsystem ist nach v1 verstanden, v2/v3 festigen die
  Übertragung auf andere Buchstaben. Zurück in beide Richtungen ist trivial (Content-Zeile ändern).

## D-012 — Jomolhari vorn in der UI-Font-Kette (2026-10-06)

- Als letzter Fallback hinter dem generischen `sans-serif` griff Jomolhari in Chrome nicht (Tofu in
  Überschriften). Dank `unicode-range` (nur U+0F00–0FFF) kann Jomolhari gefahrlos an erster Stelle
  stehen: Latein kommt weiter aus der Systemschrift.

## Sackgassen

- **Fontsource-CSS direkt importieren** → Tofu beim ersten Rendern (siehe D-009).
- **Jomolhari als letzter Fallback nach `sans-serif`** → greift nicht (D-012).
- **Headless-Screenshots ohne Interaktion** reichen für Quiz-Zustände nicht → `tools/shot.mjs` (CDP).
