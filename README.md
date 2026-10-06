# Learn Tibetan · བོད་ཡིག

Privater Prototyp einer mobilen Web-App (PWA) zum **Lesenlernen der tibetischen Uchen-Schrift**:
Zeichen sehen → eine von vier Antworten antippen → sofortiges Feedback → nächste Frage.

Umfang (v0.2): Alphabet als System in traditionellen Reihen (mit optionalen Devanagari-Parallelen),
Zeichen ↔ Wylie, Vokale, Hören → Zeichen (eigene Aufnahmen).
Vision und Planung: [`specs_plans_prompts/`](specs_plans_prompts/), Arbeitsregeln: [`AGENTS.md`](AGENTS.md).

## Schnellstart

Voraussetzungen: Node ≥ 20, [uv](https://docs.astral.sh/uv/) (nur für Content und Tests).

```bash
cd web
npm install
npm run dev          # http://localhost:5173, im WLAN auch über die angezeigte Netzwerk-URL
```

Die App braucht zur Laufzeit kein Python: Der Lerninhalt liegt fertig generiert in
`web/src/content/curriculum.json`.

## Tests

```bash
uv run pytest -q          # Referenz-Engine (62 Tests) + Content-Build
cd web && npm test        # Quiz-Engine, Distraktoren/Mehrdeutigkeit, Fortschritt, Persistenz
```

## Wie der Inhalt repräsentiert ist

```
content/curriculum.toml  ─┐  von Hand: Reihen, Buchstaben, Devanagari, Vokalzeichen,
content/audio.toml       ─┤            Verwechslungslisten, Audio-Gleichklänge, Audio-Manifest
                          ▼
uv run learn-tibetan build-content     (src/learn_tibetan/content.py)
                          ▼
web/src/content/curriculum.json        generiert, committed: Items, Gruppen, Lektionen
```

- **Getrennte Repräsentationen** pro Item: `tibetan` (Schreibung), `wylie` (EWTS), `tz`
  (deutsche Lesehilfe im Stil des Tibetischen Zentrums), `audio` (Clip mit Herkunft und Status),
  dazu `analysis` (Silbenpositionen, Grundlage für das spätere Kapitel Silbenstruktur).
- **Wylie und TZ werden nie von Hand geschrieben**, sondern beim Build erzeugt.
- Fachlich unsichere Angaben (Devanagari für ཙ ཚ ཛ, visuelle Verwechslungspaare) stehen
  kommentiert in `content/curriculum.toml` und lassen sich dort direkt korrigieren.
- Lernpfad: 22 Lektionen (pro Reihe Zeichen→Wylie und Wylie→Zeichen, drei Vokallektionen, drei
  Hörlektionen). Stellschrauben der Lernlogik: `web/src/engine/config.ts`; Schwellen pro Lektion im
  Content (`mastery`).

Nach Änderungen an `content/`: `cd web && npm run content` (bzw. `uv run learn-tibetan build-content`).

## Transliteration und TZ-Aussprache

Die Referenz-Engine liegt in `src/learn_tibetan/phonetics/` (`tz.py`, `wylie.py`). Sie stammt
unverändert aus einem internen Transferpaket (nur der Importpfad wurde angepasst), samt ihren 62
Tests. Hintergrund, Methodik und Grenzen: `references/transliteration/docs/tz-umschrift.md`.

```python
from learn_tibetan.phonetics import tz, wylie
wylie.render("སངས་རྒྱས་ཆོས།")   # sangs rgyas chos
tz.render("སངས་རྒྱས་ཆོས།")      # sang gyä tschö
```

Erzeugt wird die Variante `tz-aktuell`. Regeländerungen nur mit Test und Eintrag in
[`docs/decisions.md`](docs/decisions.md).

## Audio hinzufügen oder ersetzen

Gelernt wird ausschließlich mit **freigegebenen** Clips (`status = "approved"` in
`content/audio.toml`). Zurzeit: eigene Aufnahmen für alle 30 Buchstaben und ཨི ཨུ ཨེ ཨོ (Rohdaten in
`references/audio_files/`). KI-TTS war für Einzelbuchstaben unbrauchbar (D-013).

**Eine ganze Reihe in einer Datei** (Silben mit kurzen Pausen dazwischen):

```bash
uv run python tools/audio/curate.py split Pa.m4a l-pa l-pha l-ba l-ma --dialect "Owner-Aufnahme (TZ-Aussprache)"
cd web && npm run content
```

**Einzeldateien pro Zeichen:**

1. Pro Zeichen eine Datei aufnehmen, Dateiname = Item-ID, Format egal: `l-ka.m4a`, `l-kha.m4a`, …,
   `v-ki.m4a` (IDs: Wylie mit Präfix `l-` für Buchstaben, `v-` für Vokalformen; འ = `l-_a`, ཨ = `l-a`).
2. `uv run python tools/audio/curate.py import ~/aufnahmen --dialect "Zentraltibetisch (Lhasa)"`
   (schneidet Stille, normalisiert die Lautstärke, erzeugt mp3 in `web/public/audio/`, setzt `approved`).
3. `cd web && npm run content`

**KI-Kandidaten prüfen:** In der App unter Einstellungen → „Audio-Clips prüfen“ anhören, ✓/✗
markieren, „Änderungen kopieren“, in eine Datei einfügen und
`uv run python tools/audio/curate.py status datei.txt`, danach `npm run content`.
Klingen zwei Laute im Audio gleich, die Paare in `[audio_equivalent]` eintragen. Sie werden dann nie
gemeinsam abgefragt.

**Neue Kandidaten erzeugen** (lädt PyTorch CPU + Modell, einige hundert MB):
`uv run --group audio python tools/audio/generate.py [--items l-ka ...] [--seed 0]`.
Modell-Lizenz CC-BY-NC-4.0, also nur für private Nutzung.

## PWA bauen und installieren

```bash
cd web
npm run build        # Typecheck + Build nach web/dist (Service Worker precacht App, Font, Audio)
npm run preview      # lokal testen: http://localhost:4173
```

Ein Service Worker (Offline-Betrieb, „Zum Startbildschirm hinzufügen“) läuft nur unter
`localhost` oder **HTTPS**. Fürs Handy deshalb `web/dist/` auf einen statischen HTTPS-Host legen
(privat halten, siehe Rechte), dort einmal öffnen und über das Browsermenü installieren. Danach
funktioniert die App offline. Über `http://<LAN-IP>` läuft die App im WLAN zwar zum Ausprobieren,
offline geht sie so aber nicht.

## Projektstruktur

```
content/                 Quell-Curriculum + Audio-Manifest (TOML)
src/learn_tibetan/       Python: Content-Build, phonetics/ = Referenz-Engine
tests/                   Python-Tests
web/                     React + TypeScript + Vite PWA
  src/engine/            Quiz-Engine (pure TS): Auswahl, Distraktoren, Fortschritt
  src/screens/           Home, Quiz, Alphabet, Einstellungen, Audio-Prüfung
  public/                Font (Jomolhari, OFL), Icons, Audio
tools/                   audio/ (Kandidaten, Kuration), shot.mjs (Headless-Screenshots)
references/              internes Referenzmaterial (teilweise gitignored)
docs/                    engineering-log.md, decisions.md
specs_plans_prompts/     Specs, Pläne, Prompts
```

## Rechte

Privates Projekt. Die Referenz-Engine und `references/transliteration/` stammen aus einem Projekt
mit proprietärer Lizenz und sind nur für die interne Nutzung bestimmt. Die TZ-Scans und der
DILA-Index sind gitignored. Der Font Jomolhari steht unter SIL OFL 1.1 (`web/public/fonts/`). Die
MMS-Kandidaten-Clips stehen unter CC-BY-NC-4.0.
