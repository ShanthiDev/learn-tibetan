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
