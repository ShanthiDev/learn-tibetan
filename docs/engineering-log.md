# Engineering-Log

Ausführliches Arbeitsprotokoll. Neueste Einträge unten. Pro Eintrag: Ziel, Vorgehen, Befunde,
Probleme/Sackgassen, Ergebnis, nächster Schritt.

---

## 2026-10-06 — Sitzung 1: Aufräumen, Referenzpaket, Planung (M0)

**Ziel:** Repo aufräumen, Transferpaket einsortieren, Initial-Prompt (01_01) in eigene Spec,
Roadmap und Ausführungsprompt überführen, Arbeitsregeln festlegen. Danach Halt zur Freigabe.

**Ausgangslage:** frisches `uv init`-Projekt (Hello-World in `src/learn_tibetan/__init__.py`),
noch kein Commit, Initial-Prompt und das 48-MB-Zip `references/transliteration/…mit-quelltexten.zip`.

**Vorgehen und Befunde:**

1. `README_UMSCHRIFT.md` im Zip gelesen. Inhalt: Produktionskerne `tz.py` (TZ-Aussprache,
   stdlib-only, Version 1.0.0) und `wylie.py` (EWTS, nutzt Parser aus `tz.py`), 62 fokussierte
   Tests, Forschung/Evidenz, Reader-Integrationsbeispiel, TZ-Scans (47 MB), DILA-Index (7 MB).
   Lizenz: Ursprung proprietär, interne Nutzung.
2. Zip in den Scratchpad entpackt und einsortiert (Tabelle in
   `references/transliteration/README.md`). Engine + Tests in die Projektstruktur, Importpfad
   angepasst (D-002). Große Dateien gitignored (D-003). Original-Zip bleibt lokal liegen.
3. `pytest` per `uv add --dev pytest`: Online-Installation scheiterte (DNS-Timeouts für pypi/npm in
   WSL, auch ohne Sandbox; `curl` lieferte einmal 200, danach nur noch Resolve-Timeouts). Lösung:
   `uv add --dev pytest --offline` aus dem uv-Cache. **62 passed in 1 s** (inkl. DILA-Vergleich,
   da Index lokal vorhanden).
4. Commit `f642cbe` (Scaffold + Referenzen + Initial-Prompt); Working Tree sauber.
5. Engine-Probe für den Lernstoff:
   - Alle 30 Buchstaben: Wylie korrekt (`ka … a`, འ → `'a`, ཨ → `a`).
   - TZ (tz-aktuell) kollidiert bei ཅ/ཆ → *tscha*, ཞ/ཤ → *scha*, ཟ/ས → *sa*, འ/ཨ → *a*.
     Gebetsbuch-Variante kollabiert zusätzlich die Behauchung (ཁ → *ka*). → Mehrdeutigkeitsregel D-005.
   - Vokalformen: ཀི `ki`/`ki`, ཅི `ci`/`tschi`, ཤུ `shu`/`schu`. Zusammensetzung Buchstabe +
     Vokalzeichen funktioniert direkt mit `wylie.syllable`/`tz.render`.
   - `tz.analyse("བསྒྲུབས")` liefert alle Positionen → Grundlage für Kapitel 6 (`analysis`-Feld).
6. Kein UI-Referenzbild unter `references/ui/` vorhanden.
7. Planung geschrieben: `AGENTS.md` (+ `CLAUDE.md` importiert sie), Spec 01_02, Roadmap 01_03,
   Ausführungsprompt 01_04, `CHANGELOG.md`, `docs/decisions.md` (D-001…D-006).

**Interpretation des Auftrags:** „Nur bis Schritt 5“ = Curriculum-Kapitel 1–5. Kapitel 6/7 nur im
Datenmodell vorbereitet (im Plan als Annahme 1 markiert, Owner bestätigt bei Freigabe).

**Probleme:** DNS/Netz in WSL instabil. Für M2 (npm install) wird funktionierendes Netz gebraucht.

**Nächster Schritt:** Freigabe durch den Owner, dann M1 (Content-Pipeline).

## 2026-10-06 — Sitzung 1 (Fortsetzung): UI-Vorlage, DNS

**UI-Vorlage:** Der Owner hat `references/UI/Tibetan_Consonants_Screenshot.jpeg` ergänzt; der Ordner
heißt jetzt kleingeschrieben `references/ui/`, wie im Initial-Prompt. Inhalt: Android-App, Kopfzeile
„Home“ + „Quiz“-Button, Raster mit 4 Spalten über die volle Breite (eine Reihe pro Zeile), sehr große
Glyphen mit Tsheg, schwarzes Label-Band mit englischer Pseudo-Lautschrift in Großbuchstaben (KA, CHA,
CHHA …), Papiertextur. Für die Spec übernommen: Raster, Größe, Klarheit. Abweichend: Wylie statt
Pseudo-Lautschrift (die Vorlage nennt ཅ „CHA“, in Wylie ist das `cha` = ཆ, genau die Verwechslung,
die wir vermeiden wollen), Palette statt Schwarz, Gruppen-Header. Spec 01_02 §8/§12 aktualisiert.

**DNS:** Ursache bestätigt per Roh-DNS-Abfrage aus Python: `1.1.1.1` antwortet, der WSL-Resolver
`10.255.255.254` (DNS-Tunneling) läuft in einen Timeout. Zum Umstellen von `/etc/resolv.conf` braucht
es sudo mit Passwort; das macht der Owner. Befehle siehe Antwort an den Owner bzw. Memory.

## 2026-10-06 — Sitzung 2: M1 Content-Pipeline

**Ziel:** Quell-Curriculum + Build → statisches JSON für die App (Spec §3–§5).

**Vorgehen:**
- DNS vom Owner auf Cloudflare umgestellt (`/etc/resolv.conf`, `generateResolvConf = false`);
  npm/pypi wieder erreichbar.
- `content/curriculum.toml`: 8 Gruppen (Labels/Zweitlabels nach Spec), Devanagari sicher für Reihen
  1–4, ཝ, ཡ–ཨ; ཙ ཚ ཛ nur mit Notiz („schreibt in Sanskrit च/छ/ज“), ཞ ཟ འ ohne Entsprechung.
  Vokale a/i/u/e/o mit tibetischen Namen. Verwechslungslisten visuell/Wylie als vorläufig markiert.
  `content/audio.toml` leer (Format im Kommentar).
- `src/learn_tibetan/content.py`: Buchstaben + Vokalformen (Buchstabe + Vokalzeichen, NFC) →
  `wylie.syllable`, `tz.render(…, "tz-aktuell")`, `tz.analyse` → Items. Lektionen nach Spec §5.
  CLI `learn-tibetan build-content` ersetzt das uv-Hello-World.
- `tests/test_content.py`: Reihenfolge/Gruppen, Stichproben ཅ = ca/tscha/च, ཀི, 'a vs a,
  Lektionen referenzieren existierende Items. 3 passed.

**Entscheidungen im Kleinen:**
- IDs `l-<wylie>` / `v-<wylie>`, Apostroph → `_` (འ = `l-_a`, ཨ = `l-a`).
- Buchstaben tragen `vowel = "a"` und `baseId = self`, damit Vokallektionen Buchstabe + Vokalformen
  als eine Familie behandeln können (Distraktoren „gleicher Grundbuchstabe“).
- Kein `generatedAt` in `meta` (abweichend von Spec §4): deterministische Ausgabe, keine
  Diff-Rauschen bei jedem Build. Stattdessen Engine-Versionen.
- `wylie.py` hat keine eigene Version → `wylie: "transfer-2026-10-06"`.

**Ergebnis:** `curriculum.json` 66 KB, 150 Items, 22 Lektionen.

**Nächster Schritt:** M2 Web-Gerüst.

## 2026-10-06 — Sitzung 2: M2 Web-Gerüst, Alphabet, PWA

**Vorgehen:**
- `web/` von Hand aufgesetzt (kein interaktives `create-vite`): `package.json` mit Skripten `dev`,
  `build` (tsc + vite), `preview`, `test`, `content` (ruft die Python-Pipeline).
- Font-Vergleich Noto Serif Tibetan vs. Jomolhari per Headless-Chrome-Screenshot → Jomolhari (D-007).
- Struktur: `content/index.ts` (Typen + Lookups über das generierte JSON), `storage.ts` (versionierte
  localStorage-Helfer), `settings.tsx` (Context), `router.ts` (Hash-Router, ~20 Zeilen), `ui.tsx`
  (TopBar, `Tib` mit optionalem Tsheg), Screens Home (vorläufig), Alphabet, Settings.
- Alphabet nach UI-Vorlage: 4er-Raster pro Reihe, Glyphe mit Tsheg, dunkles Label-Band mit Wylie
  (Mono), darunter optional TZ/Devanagari; Gruppen-Header in Robenrot; Detail-Sheet mit Escape/Backdrop.
- Icons per Headless-Chrome aus der Font gerendert (192/512/Favicon), 3 Iterationen bis zur Zentrierung.
- PWA-Build: `precache 12 entries (637 KiB)`, `sw.js` erzeugt.

**Befunde/Probleme:**
- Erster Screenshot: Tsheg brach unter die Glyphe, weil `.cell-glyph` ein Grid war (Text und Tsheg
  wurden zwei Grid-Items) → Flex mit `align-items: baseline`. Jomolhari-Glyphen sind klein im em →
  Rastergröße von 15vw auf 22vw erhöht.
- Offline-Test im Headless-Chrome nicht trivial (bräuchte CDP); Workbox-Precache ist erzeugt,
  **manuelle Bestätigung auf dem Handy steht aus** (Owner).

**Nächster Schritt:** M3 Quiz-Engine + Kapitel 2/3.

## 2026-10-06 — Sitzung 2: M3 Quiz-Engine + Kapitel 2/3 → v0.1.0

**Vorgehen:**
- Engine als pure Funktionen: `config.ts` (alle Stellschrauben), `rng.ts` (mulberry32 + shuffle),
  `progress.ts` (Box 0–5, falsch −2 + Retry nach 2–3 Fragen, Lektionsscore/-meisterung, lineare
  Freischaltung), `question.ts` (Distraktoren mit Prioritätsstufen je Modus/Scope, P/A-Mehrdeutigkeitsregel,
  Audio-Schlüssel mit `audioEquivalent`), `select.ts` (Pool je Session-Art, gewichtete Auswahl
  `(6−box)²`, neue ×2, letzte 2 ausgeschlossen, fällige Fehler zuerst).
- Tests (8, auf Anhieb grün): 4 eindeutige/unzweideutige Antworten für alle 150 Items × 2 Richtungen,
  Reihen-Priorität (ཅ → ca/cha/ja/nya), Vokal-Distraktoren gleicher Grundbuchstabe, Audio-Äquivalenz
  schließt ཆ aus, Box-Update/Retry, Wiederkehr nach 2–3 Fragen, Freischaltung, Storage-Roundtrip.
- UI: Progress-Context, Router mit Parameter, `lessons.ts` (abgeleiteter Pfadstatus), Home mit
  Lernpfad, Quiz mit Intro-/Frage-/Feedback-/Abschluss-/Leer-Phase.

**Befunde/Probleme (per Screenshot gefunden):**
1. Tofu bei der großen Prompt-Glyphe → Font selbst gehostet, `font-display: block`, Preload (D-009).
2. Lernpfad als Liste von 22 langen Titeln unübersichtlich → pro Reihe eine Zeile mit Glyphen und
   zwei kompakten Richtungs-Buttons („ཀ → ka“, „ka → ཀ“) inkl. Mini-Fortschritt.
3. 🔒-Emoji im Headless ohne Emoji-Font → kleines Inline-SVG.
4. Tibetisch in UI-Labels als Tofu → Jomolhari als letzter Fallback der UI-Font-Kette.
5. Interaktion verifiziert mit neuem `tools/shot.mjs` (CDP über Node-24-WebSocket, keine
   Abhängigkeit): Intro → falsche Antwort (rot, richtige gold, „ཀ = ka“) → Auto-Weiter → richtige
   Antwort (gold), Zähler 1/2, Fortschrittsbalken wächst.

**Offen:** Offline-Test auf dem Handy (Owner). Haptik nur auf echten Geräten prüfbar.

**Nächster Schritt:** M4 Vokale (Lektionen 17–19 sind dank generischer Engine bereits spielbar;
es fehlen Feinschliff und ein Testfall).

## 2026-10-06 — Sitzung 2: M4 Vokale

**Vorgehen:** Vokallektionen waren mit M3 bereits spielbar (generische Engine, Scope `syllables`,
Distraktoren gleicher Grundbuchstabe; Test aus M3 deckt das ab). Beim Durchrechnen der
Meisterungsschwelle fiel der Aufwand von v2/v3 auf (480/900 richtige Antworten) → D-011: optionales
`mastery {box, share}` je Lektion (Python-Content + `lessonScore`), v2/v3 nur Leserichtung. Neuer
Test für die Share-Schwelle (9 Vitest-Tests grün).

**Befunde (Screenshots):** Vokal-Intro zeigte ཀ in der Überschrift als Tofu → Ursache: Jomolhari als
letzter Fallback hinter `sans-serif` wird nicht genutzt; Lösung D-012. Label-Bänder unterschiedlich
hoch, wenn eine Zeile umbricht („inhärentes a“) → `flex: 1` im Band.

**Nächster Schritt:** M5 Audio, beginnend mit dem MMS-TTS-Spike.

## 2026-10-06 — Sitzung 2: M5 Audio → v0.2.0

**Spike MMS-TTS:** HF-API: Modell verfügbar, CC-BY-NC-4.0, Tokenizer mit tibetischen Zeichen
(kein uroman), Tsheg = Pad-Token (id 0). uv-Gruppe `audio` mit CPU-Torch-Index (vermeidet CUDA-
Pakete), `transformers` 5.18. Erste Generierung: alle Clips 0,08–0,53 s. Messreihe mit Varianten
(Tsheg, Shad, Leerzeichen, Wiederholung, `speaking_rate` 0,6/0,4, Trägerwort ཀ་བ, Satz) → nur
ganze Sätze haben natürliche Silbenlängen. Ich kann Audio nicht anhören; Messung = Dauer + Anzahl
stimmhafter Segmente. Fazit D-013. Wikimedia-Commons-Suche: nichts Passendes.

**Umsetzung:**
- `tools/audio/curate.py` (stdlib): Manifest lesen/schreiben, `import` (ffmpeg: Stille trimmen,
  `loudnorm`, mono mp3 48 kbit/s, `source = manual`, `status = approved`), `status` (Prüfergebnisse).
  `generate.py` nutzt dessen Helfer, schützt approved/rejected/manual vor Überschreiben.
- App: `hasAudio()` = nur `approved` (Engine: Pool, Lektionen, Distraktoren), `audio.ts`
  (gecachte `HTMLAudioElement`s), `AudioButton`, Audio-Prompt im Quiz (Auto-Play, Leertaste),
  Vorspielen nach Antwort, Prüfansicht `#/audio-review` mit ✓/✗ und „Änderungen kopieren“
  (Fallback: Text anzeigen, falls Clipboard nicht verfügbar, z. B. http auf dem Handy).
- Verifikation: vier Clips temporär freigegeben → Lektion a1 spielbar (Play-Button, Glyphen-Antworten),
  Prüfansicht korrekt; danach Manifest zurückgesetzt. PWA precacht jetzt 46 Einträge (717 KiB).

**Offen für den Owner:** Clips in der Prüfansicht anhören (vermutlich alle verwerfen), eigene
Aufnahmen machen bzw. besorgen, `audio_equivalent` nach dem Anhören füllen.

**Nächster Schritt:** M6 README/Abschlussdoku.

## 2026-10-06 — Sitzung 2: M6 Abschlussdoku und Retrospektive

**Vorgehen:** README komplett (Schnellstart, Tests, Content-Modell, Engine, Audio-Workflows, PWA
inkl. HTTPS-Hinweis fürs Handy, Struktur, Rechte). Gesamtsuite einmal: Python 65 passed, Vitest 9
passed, Build ok (46 Precache-Einträge, 717 KiB). Roadmap 01_03 um den Stand ergänzt.

**Retrospektive:**
- *Gut:* Content-Pipeline mit generiertem Wylie/TZ hat sich gelohnt; Vokallektionen kosteten fast
  nichts zusätzlich. Die allgemeine P/A-Mehrdeutigkeitsregel deckt Audio-Gleichklang ohne
  Sonderfälle ab. Screenshots per Headless-Chrome (`tools/shot.mjs`) haben fünf echte UI-Fehler
  gefunden (Tofu ×2, Tsheg-Umbruch, Glyphengröße, Bandhöhen), die Unit-Tests nie gesehen hätten.
- *Lehre:* Font-Fallback für eine Schrift, die Systemfonts nicht haben, braucht `font-display: block`
  und den Font vorn in der Kette (mit `unicode-range`). Meisterungsschwellen vor dem Bauen
  durchrechnen (v2/v3 wären sonst endlos gewesen).
- *Grenze:* Audioqualität kann der Agent nicht beurteilen; dort ist der Owner im Loop (Prüfansicht).

**Offene Punkte / nächste Planungsgrundlage (Kapitel 6/7):**
1. Owner: Offline-/Installationstest auf dem Handy (HTTPS-Host), Haptik, Lesbarkeit der Glyphen.
2. Owner: echte Audioaufnahmen (34 Clips), danach `audio_equivalent` füllen.
3. Owner: visuelle Verwechslungspaare in `content/curriculum.toml` fachlich prüfen.
4. Kapitel 6: Silben-Items (`kind: 'syllable'`) aus einer kleinen Silbenliste; `analysis` ist schon
   generiert. Neue Ansicht „Silbe zerlegen“ (Positionen farbig) und Quizmodus „Wurzelbuchstabe finden“.
   Distraktor-Scope `syllables` erweitern (gleiche Wurzel/anderer Präfix usw.).
5. Kapitel 7: einfache Wörter mit Kontrast Schreibung / Wylie / TZ; hier wird die TZ-Anzeige im
   Quiz relevant (TZ → Zeichen nur mit der Mehrdeutigkeitsregel).

## 2026-10-06 — Sitzung 3: Owner-Aufnahmen, Halt nach Fehler

**Owner-Feedback nach dem ersten PC-Test:** „sieht super aus“; MMS-Clips weitgehend unbrauchbar
(bestätigt D-013); eigene Aufnahmen geliefert; nach falscher Antwort soll das Quiz anhalten
(Weiter per Knopf), Vorbild Duolingo, gern mit Ton.

**Audio:**
- Zip: 10 m4a (AAC, 44,1 kHz mono), pro Datei eine Reihe: Ka, Ca, Ta, Tsa, Sha (= ཞ-Reihe), Ra, Ha,
  „Ii uu ee oo“, „Khikhu shapkyu drengbu naro“ (Vokalnamen), „Me chu ri so“. Die Pa-Reihe fehlte und
  kam als `Pa.m4a` nach.
- Segmentierung (eigener Energie-Detektor, stdlib + ffmpeg): überall 4 Silben (Ha 2), plus Klicks/Atmer
  in Ca, Tsa, Pa. Plausibilisierung per Nulldurchgangsrate am Silbenanfang: Zischlaute genau dort, wo
  erwartet (Ra: sa 10800/s; Sha: zha/za; Ca: cha/ja); „Me chu ri so“ = me/chu/ri/so (Pos. 2, 4 zischend).
- `curate.py split` gebaut und angewandt: 34 Clips (30 Buchstaben + ཨི ཨུ ཨེ ཨོ), Störgeräusche korrekt
  verworfen. MMS-Reste samt Dateien entfernt. Lektion a3 → Vokale auf ཨ. Extras als Segmente (D-016).
- Panne: `pkill -f "vite preview …"` traf die eigene Shell (Muster stand in deren Befehlszeile) →
  Abbruch vor Doku/Commit. Richtig: `pkill -f "[v]ite preview …"`.

**Fehler-Feedback (D-015):** Panel „Oops, nicht ganz.“ unter den Antworten (Layout schrumpft die
Glyphe statt zu überdecken, damit die markierte richtige Antwort sichtbar bleibt), richtige Lösung +
eigene Wahl + TZ + Anhören, „Weiter“ mit Autofokus (Enter/Leertaste). Kein Timer mehr bei Fehlern,
Tippen auf den Hintergrund überspringt nichts mehr. `sfx.ts`: zwei synthetisierte Töne (G5→D6 für
richtig, B♭3→F3 Dreieck für falsch); Aussprache folgt 380 ms nach dem Ton. Headless verifiziert:
Panel steht nach 2,5 s noch, „Weiter“ → nächste Frage.

**Offen / Frage an den Owner:** Sollen tonale Paare (ཞ/ཤ, ཟ/ས, འ/ཨ) als Audio-Gleichklang gelten
(nie gemeinsam in einer Hörfrage)?
