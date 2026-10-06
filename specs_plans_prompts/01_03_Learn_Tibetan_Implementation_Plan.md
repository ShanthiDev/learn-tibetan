# 01_03 — Learn Tibetan: Implementierungsplan / Roadmap (MVP, Kapitel 1–5)

**Stand:** 2026-10-06 · Spec: `01_02_Learn_Tibetan_Spec.md` · Regeln: `AGENTS.md`

Jeder Meilenstein endet mit: betroffene Tests grün → CHANGELOG + engineering-log (+ decisions) →
Commit → sauberer Working Tree. Die App ist ab M2 jederzeit lauffähig.

## M0 — Aufräumen und Planung ✅ (2026-10-06)

- Transferpaket entpackt und einsortiert, große Dateien gitignored, Engine nach
  `src/learn_tibetan/phonetics/`, 62 Referenztests grün.
- AGENTS.md, CLAUDE.md, CHANGELOG.md, docs/engineering-log.md, docs/decisions.md, Specs 01_02–01_04.

## M1 — Content-Pipeline

- `content/curriculum.toml`: 8 Gruppen/30 Buchstaben, Devanagari (+ Notizen), Vokalzeichen,
  Verwechslungslisten, leere `audio_equivalent`.
- `content/audio.toml` (anfangs leer).
- `src/learn_tibetan/content.py`: TOML laden → Items (Buchstaben + 150 Vokalformen) mit
  generiertem `wylie`, `tz`, `analysis` → Lektionen nach Spec §5 → `web/src/content/curriculum.json`.
  CLI `learn-tibetan build-content` (ersetzt das uv-Hello-World in `__init__.py`).
- `tests/test_content.py` (eine Datei, Spec §11).
- **Fertig, wenn:** JSON erzeugt, Test grün, Stichprobe ཅ → `ca`/`tscha`, ཀི → `ki`.

## M2 — Web-Gerüst, Alphabet-Referenz, PWA

- `web/` mit Vite + React + TS, Vitest, `vite-plugin-pwa`. npm-Skript `content` ruft die Python-Pipeline.
- Theme (CSS-Variablen, Palette), Font selbst gehostet (Noto Serif Tibetan vs. Jomolhari kurz
  vergleichen, Entscheidung + Lizenz in decisions.md, OFL-Text neben die Font-Datei).
- Kleiner Router (Home, Alphabet, Settings, Quiz), Settings-Context mit localStorage.
- Alphabet-Referenz (Kapitel 1) inkl. Detailansicht, Devanagari-/TZ-Schalter.
- PWA: Manifest, Icons (SVG-basiert, PNG falls nötig per ImageMagick), Precache inkl. Font.
- **Fertig, wenn:** `npm run dev` zeigt Home + Alphabet auf Handy-Viewport schön; `npm run build`
  erzeugt Service Worker; offline per `preview` einmal manuell bestätigt.

## M3 — Quiz-Engine + Kapitel 2/3 (Kernerlebnis)

- `web/src/engine/`: `config.ts`, `rng.ts`, `progress.ts` (Box-Update, Fehler-Warteschlange,
  Lektion gemeistert), `select.ts` (gewichtete Auswahl), `question.ts` (Distraktoren +
  Mehrdeutigkeitsregel), `storage.ts`.
- Quiz-Screen mit Spec-§8-Verhalten (Auto-Advance, Fehleranzeige, Tastatur, Haptik, kein
  Doppel-Submit), Intro-Karten, Freischaltung, „Alles üben“, „Schwieriges wiederholen“, Reset.
- Vitest: `question.test.ts`, `progress.test.ts`, `storage.test.ts`.
- **Fertig, wenn:** Reihe 1 lässt sich auf dem Handy flüssig durchspielen; Lektionen 1–16
  freischaltbar; Tests grün. → Version **0.1.0** im CHANGELOG.

## M4 — Kapitel 4: Vokale

- Lektionen 17–19 aktiv, Vokal-Intro-Karte (Vokalzeichen auf ཀ, Namen gi gu / zhabs kyu / 'greng bu /
  na ro), Distraktoren nach gleichem Grundbuchstaben.
- Referenzansicht: Vokalzeile.
- **Fertig, wenn:** Vokallektionen spielbar, Distraktor-Test um einen Vokalfall ergänzt.

## M5 — Kapitel 5: Audio

1. **Spike (zeitlich begrenzt):** `facebook/mms-tts-bod` prüfen: Verfügbarkeit, Lizenz,
   Eingabeformat (Tibetisch direkt oder romanisiert?), Klang bei Einzelbuchstaben vs. Trägersilbe.
   Ergebnis in decisions.md, auch wenn negativ (dann Sackgasse dokumentieren).
2. `tools/audio/generate.py` (uv-Gruppe `audio`): erzeugt Kandidaten in `tools/audio/candidates/`
   (gitignored), Konvertierung nach mp3/ogg (ffmpeg, falls vorhanden), Übernahme ausgewählter Clips
   nach `web/public/audio/` + Manifest-Eintrag `status = "candidate"`.
3. App: `audio.ts`, Play-Buttons in Referenz/Intro, Modus `audio-tib`, Lektionen 20–22,
   Audio-Prüfansicht, Precache der Clips.
4. `audio_equivalent` mit den beim Anhören festgestellten Gleichklängen füllen.
- **Fertig, wenn:** Audio-Lektion mit mindestens Reihe 1–4 spielbar oder, falls TTS untauglich,
  Pipeline + Prüfansicht fertig und manuelle Aufnahmen dokumentiert eingeplant. → Version **0.2.0**.

## M6 — Abschlussdoku

README: App starten, Tests, Content-Repräsentation, Transliteration/TZ-Generierung,
Audio hinzufügen/ersetzen, PWA bauen/installieren. Kurze Retrospektive im engineering-log,
offene Punkte für Kapitel 6/7 als nächste Planungsgrundlage.

## Risiken

| Risiko | Umgang |
|---|---|
| DNS/Netz in WSL fällt zeitweise aus (npm/pypi nicht erreichbar) | Retry; Python offline aus Cache; ggf. Owner bitten, das Netz zu prüfen |
| MMS-TTS ungeeignet für Einzelbuchstaben oder Lizenz unpassend | Trägersilben, manuelle Aufnahmen; Audio-Kapitel nicht blockierend für M1–M4 |
| Tibetan-Font rendert Stapel/Vokale schlecht | Font-Vergleich in M2 mit Vokalformen und einem Stapel (བསྒྲུབས) |
| Verwechslungslisten fachlich ungenau | vorläufig, in Daten, leicht korrigierbar |
