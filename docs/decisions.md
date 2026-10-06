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

## D-013 — MMS-TTS nur als Kandidatenquelle; Einzelbuchstaben untauglich (2026-10-06)

- **Geprüft:** `facebook/mms-tts-bod` (Rev. `e5767a9`), verfügbar, nicht gated, Lizenz
  **CC-BY-NC-4.0** (privat ok, nicht veröffentlichen), VITS, Eingabe direkt in tibetischer Schrift
  (`is_uroman: false`), 16 kHz.
- **Befund (gemessen, nicht gehört):** Einzelbuchstaben ergeben 0,08–0,16 s, Vokalformen 0,13–0,19 s,
  auch mit Tsheg, Shad, Leerzeichen, Wiederholung (ཀ་ཀ་ཀ་ 0,19 s), langsamer `speaking_rate`
  (0,4 → 0,18 s) oder echtem Wort (ཀ་བ 0,16 s). Ein Satz (བཀྲ་ཤིས་བདེ་ལེགས།) ergibt normale
  ~0,45 s/Silbe. Ursache u. a.: Der Tsheg ist im Tokenizer das **Pad-Token** → Silbengrenzen gehen verloren.
- **Entscheidung:** Kandidaten werden erzeugt und mitgeliefert (34 Clips, winzig), aber Lernen und
  Referenz verwenden **nur freigegebene** Clips. Kuratiert wird in der Prüfansicht. Echte Clips
  kommen voraussichtlich aus eigenen Aufnahmen (Owner/Lehrer) über `curate.py import`.
- **Nicht weiter verfolgt:** Silbe aus einem Trägersatz herausschneiden (ohne Abhören nicht
  validierbar), Wikimedia Commons (keine tibetischen Buchstaben-Aufnahmen gefunden).

## D-014 — Audio-Kuration über Prüfansicht + Skript statt In-App-Recorder (2026-10-06)

- Prüfansicht speichert Markierungen lokal und kopiert sie als `item status`-Zeilen;
  `curate.py status <datei>` schreibt sie ins Manifest. Eigene Aufnahmen (beliebiges Format,
  Dateiname = Item-ID) importiert `curate.py import <ordner>`.
- Ein In-App-Recorder wäre bequemer, ist aber Scope-Erweiterung (Dateien müssten trotzdem ins Repo).

## D-015 — Nach falscher Antwort Halt bis „Weiter“ (2026-10-06, Owner-Wunsch)

- **Änderung gegenüber 01_01/01_02:** Dort hieß es „kein Weiter-Button“. Für **richtige** Antworten
  bleibt das so (Auto-Weiter nach 350 ms). Bei **falschen** Antworten stoppt das Quiz: Panel unten
  (Duolingo-Vorbild) mit richtiger Lösung, eigener Wahl, TZ und Audio, Weiter nur per Button/Enter.
- **Begründung (Owner):** Ein Fehler braucht einen bewussten Moment; Auto-Weiter war zu schnell.
- Töne per Web Audio synthetisiert (keine Dateien, kein Precache-Ballast), abschaltbar.

## D-016 — Owner-Aufnahmen als Audioquelle, Reihen-Aufnahmen werden automatisch geschnitten (2026-10-06)

- Rohaufnahmen in `references/audio_files/` (Zip + `Pa.m4a`, committed, ~1,2 MB, eigenes Material).
  Pro Datei eine Reihe; Zuordnung per Dateiname, akustisch plausibilisiert (Nulldurchgangsrate am
  Silbenanfang: Zischlaute an den erwarteten Positionen).
- `curate.py split`: Energie-Segmentierung (20-ms-Fenster, Schwelle 30 dB unter dem lauten Ende,
  Pause ≥ 180 ms), überzählige Segmente = die leisesten (Klicks/Atmer 44–58 dB vs. Silben 70–81 dB),
  80 ms Vorlauf, 120 ms Nachlauf, Fades, `dynaudnorm`, mp3 64 kbit/s.
- „Me chu ri so“ enthält wirklich *me chu ri so* (Zischlaut-Anlaute an Pos. 2 und 4). Vokalnamen und
  diese Wörter liegen als Segmente in `references/audio_files/segments/` (für Kapitel 7, nicht ausgeliefert).

## D-017 — Audio-URLs mit Inhalts-Hash (2026-10-06) — *war nicht die Ursache, siehe D-020*

- **Problem:** Owner hörte in den Hörübungen nichts, obwohl die Clips korrekt sind (Pegel geprüft,
  Wiedergabe per echtem CDP-Klick verifiziert). Ursache sehr wahrscheinlich: Die Owner-Aufnahmen
  ersetzten die MMS-Schnipsel (0,1 s) unter **gleichem Dateinamen**; ein offener Tab behielt die
  gecachten `HTMLAudioElement`s bzw. der Service Worker die alte Precache-Version.
- **Entscheidung:** Der Content-Build hängt `?v=<sha1[:8]>` an jede Audio-URL; Workbox ignoriert
  den Parameter `v` beim Precache-Matching (`ignoreURLParametersMatching`), offline bleibt intakt.

## D-018 — Ausspracheinfos als Daten, sichtbar nur auf Nachfrage (2026-10-06)

- Pro Buchstabe `aspiration`, `tone`, `hint_de` in `content/curriculum.toml`; Vokale mit
  `sound_de`, gesprochenem Namen, Beispielwort; allgemeine `[[topics]]`. Alles in eigenen Worten;
  die Vorlage (`references/texts/`, Webseite eines Tibetisch-Kurses) ist gitignored.
- Fachliche Basis: Lhasa-/Exil-Aussprache („Kha-Aussprache“: ག ཇ ད བ behaucht, tiefer Ton), mit
  Hinweis auf die verbreitete g/dsch/d/b-Aussprache, die auch Wylie und TZ abbilden.
- UI: ⓘ-Toggles (Pflaume als Akzentfarbe), nie dauerhaft sichtbar. Im Oops-Panel vergleicht ⓘ
  richtige und gewählte Antwort, denn dort entsteht die Frage „Was ist der Unterschied?“.
- Tonale Paare (ཞ/ཤ, ཟ/ས, འ/ཨ) bleiben im Hörquiz unterscheidbar (Owner-Entscheidung);
  `audio_equivalent` bleibt leer.

## D-019 — Zwei Aussprachevarianten für ག ཇ ད བ (2026-10-06, Owner-Vorschlag)

- Owner nimmt beide Varianten auf: A (Lhasa/Exil: wie ཁ ཆ ཐ ཕ, tiefer Ton) und B (weich g, dsch, d, b).
- Manifest: optionales Feld `variant = "A" | "B"`; Schlüssel `item#variant`. Content-Build legt
  `audioVariants` neben `audio` (Standard ohne Variante). Laufzeit: Einstellung `variant` wählt den
  Clip, fehlt er, wird der Standardclip gespielt. Engine/Distraktoren unverändert (ein Item bleibt ein Item).
- Die TZ-Umschrift (ga, dscha, da, ba) sagt nichts über die gesprochene Variante: Das TZ-Methodik-
  dokument nennt sie selbst „eher ein tiefes, weiches k/t/p“ und schreibt g/d/b nur zum Wiedererkennen.
- Versuch, die Variante der vorhandenen Aufnahmen per Voice-Onset-Time zu messen: zu unzuverlässig
  (Atem vor der Silbe verfälscht den Lautbeginn, z. B. པ 235 ms) → nicht verwendet.

## D-020 — Wiederholungsanteil in Lektionen fest begrenzt (2026-10-06)

- **Problem:** Owner hörte in „Hören“ nichts, im Alphabet aber schon. Ursache: Der Pool einer Lektion
  enthielt alle früheren Lektionen (bei „Alle freischalten“ ~300 Lese-Einträge) mit gleichem Gewicht
  wie die 16 Hörfragen (neue ×2 half kaum) → ~90 % stumme Lesefragen. D-017 (Cache) war eine
  plausible, aber falsche Vermutung; der Hash bleibt trotzdem sinnvoll.
- **Entscheidung:** `pickNext` wählt mit Wahrscheinlichkeit `reviewShare = 0.2` aus der Wiederholung,
  sonst aus den Items der Lektion; innerhalb jeweils nach Schwäche gewichtet. `newWeight` entfällt.
- **Lehre:** Bei „hört nichts“ zuerst den echten Nutzerpfad nachspielen (hier: alle freigeschaltet,
  Einstieg über Home) statt die Technik isoliert zu prüfen.

## D-021 — Zweistufiges Antworten und Übungs-Layout (2026-10-06, Owner-Wunsch)

- **Ablauf:** Option antippen = auswählen + Aussprache der Option hören; „Prüfen“ wertet. Bei
  Hörfragen kein Anhören der Optionen (würde die Antwort verraten). Richtig: „✓ Richtig“ im Button,
  Auto-Weiter; falsch: Oops-Panel mit „Weiter“ (D-015), dort wird die richtige Aussprache gespielt.
  Änderung gegenüber 01_01 („tap → feedback“): bewusst, weil das Anhören vor dem Festlegen Lernwert hat.
- **Design:** Rot für Struktur (Kopfleiste wie im Rest der App), Safran für die Aktion („Prüfen“,
  Auswahlrahmen), Gold-Doppellinie um das Prompt-Feld. Kein Rahmen um die ganze Seite (auf dem Handy
  zu eng, zu viel Rot). Rot als Prüfen-Farbe verworfen: zu laut neben der roten Kopfleiste.

## Sackgassen

- **Fontsource-CSS direkt importieren** → Tofu beim ersten Rendern (siehe D-009).
- **Jomolhari als letzter Fallback nach `sans-serif`** → greift nicht (D-012).
- **MMS-TTS für Einzelbuchstaben/-silben** → 0,1-s-Schnipsel, Tsheg = Pad-Token (D-013). Nicht erneut mit
  anderen Eingabetricks versuchen, ohne die Ergebnisse anhören zu können.
- **`pkill -f <muster>` mit dem Muster im eigenen Befehl** beendet die eigene Shell → `[v]ite`-Trick.
- **Variante (behaucht/weich) automatisch aus den Aufnahmen messen** (VOT mit Energie-/Autokorrelations-
  Heuristik) → widersprüchliche Werte; nur mit sauberen, atemfreien Aufnahmen oder per Ohr entscheidbar.
- **„Kein Ton“ als Cache-Problem behandelt** (D-017), ohne den Nutzerpfad nachzuspielen → falsche Spur (D-020).
- **`shot.mjs` mit festem Debug-Port**: Nach einem Absturz lief der alte Browser weiter, spätere Läufe
  hingen sich an ihn (alter Build per Service Worker, alter Fortschritt) → zufälliger Port, frisches
  Profil, Aufräumen bei Fehlern. Ergebnisse aus solchen Läufen nie als Beleg werten.
- **Headless-Screenshots ohne Interaktion** reichen für Quiz-Zustände nicht → `tools/shot.mjs` (CDP).
